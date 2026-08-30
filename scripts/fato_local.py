#!/usr/bin/env python3
"""
ONDE O FATO ACONTECEU — e as quatro outras coisas que não são isso.

Cicatrizes importadas do Sintonia Brasil. Não o schema dele: as leis. O Brasil
mediu falso positivo vindo de endereço da fonte, rodapé, local de evento, área
comercial, região econômica, "moro em…", lista territorial e substring acidental.
Cada uma dessas viraria, sem portão, uma afirmação sobre onde a doença está.

QUATRO ESPÉCIES DE LUGAR, E NENHUMA PROMOVE A OUTRA
-----------------------------------------------------
    BASE       onde a pessoa ou entidade está estabelecida
    OPERATING  onde ela atua
    INFLUENCE  onde está a audiência dela
    FACT       onde o acontecimento relatado ocorreu

    BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT

No LinkedIn, `basic_info.location` é no máximo candidato a BASE. Nunca FACT. Um
pesquisador baseado em Foggia, de instituição em Roma, falando da Toscana sobre
um foco constatado em Grosseto, tem QUATRO lugares verdadeiros ao mesmo tempo —
e nenhum deles substitui outro.

MENÇÃO NÃO É FATO
------------------
    PLACE_MENTION ≠ FACT_LOCATION

Achar um topônimo no texto não localiza nada. FACT exige relação semântica entre
ACONTECIMENTO e LUGAR, sustentada por linguagem — "constatata a", "sintomi
osservati in", "campioni positivi provenienti da". Preposição e proximidade de
palavras não bastam: "convegno a Bologna" tem preposição e proximidade, e não
diz nada sobre onde a doença está.

PRECISÃO É PARTE DO FATO
-------------------------
Se a fonte prova Toscana, não se inventa Grosseto. Se prova Grosseto, não se
reduz para Itália. `GEO_PRECISION` viaja com `FACT_LOCATION`, sempre.

UM CONTEÚDO, 0..N LUGARES
--------------------------
"campioni positivi provenienti da Grosseto, Siena e Arezzo" são TRÊS localizações
do fato, cada uma com sua evidência. Ficar com a primeira cidade encontrada
inventaria um recorte que a fonte não fez.

OCORRÊNCIA NÃO É INCIDÊNCIA
----------------------------
"amostras positivas recebidas de X" sustenta OCORRÊNCIA OBSERVADA. Não sustenta
incidência, prevalência nem pressão na região inteira. Por isso `TYPE_OF_EVIDENCE`
é preservado e as espécies **não se somam**.

TEMPO DO FATO NÃO É DATA DA PUBLICAÇÃO
----------------------------------------
Um post de 20/04 pode falar da semana passada, de março, ou da safra 2025/26.
`PUBLISHED_AT` e `FACT_TIME` são campos diferentes, e `FACT_TIME` só existe com
evidência própria.

    PUBLISHED_AT ≠ FACT_TIME
    ROW_PROVENANCE ≠ VALUE_PROVENANCE
    TERRITORIAL_LIST ≠ FACT_LIST
    GEOTAG ≠ FACT_LOCATION
"""
import re
import unicodedata

# ---------------------------------------------------------------- espécies
BASE, OPERATING, INFLUENCE, FACT = 'BASE', 'OPERATING', 'INFLUENCE', 'FACT'
ESPECIES = (BASE, OPERATING, INFLUENCE, FACT)

# --------------------------------------------------------------- precisão
COUNTRY, REGION, PROVINCE = 'COUNTRY', 'REGION', 'PROVINCE'
MUNICIPALITY, LOCALITY, COORDINATE = 'MUNICIPALITY', 'LOCALITY', 'COORDINATE'
OTHER_PRECISION, NOT_KNOWN = 'OTHER', 'NOT_KNOWN'
PRECISOES = (COUNTRY, REGION, PROVINCE, MUNICIPALITY, LOCALITY, COORDINATE,
             OTHER_PRECISION, NOT_KNOWN)

# ------------------------------------------------------- tipo de evidência
FIELD_OBSERVATION = 'FIELD_OBSERVATION'
DIAGNOSTIC_SAMPLE = 'DIAGNOSTIC_SAMPLE'
OFFICIAL_OCCURRENCE = 'OFFICIAL_OCCURRENCE'
CONFIRMED_FOCUS = 'CONFIRMED_FOCUS'
REGIONAL_STATEMENT = 'REGIONAL_STATEMENT'
# Saída de modelo previsional. Um mapa de risco não é um sintoma visto: é uma
# previsão sobre onde ele PODE estar. Num boletim real, "Rischio attacchi
# septoriosi in Friuli Venezia Giulia" estava sendo classificado como observação
# de campo — e o mesmo boletim, na frase seguinte, distingue as duas coisas:
# "dai rilievi in campo è emerso che ... si osservano dei sintomi evidenti".
#
#     SINTOMA OBSERVADO ≠ RISCO MODELADO
MODELLED_RISK = 'MODELLED_RISK'
OTHER_EVIDENCE = 'OTHER'
TIPOS_DE_EVIDENCIA = (FIELD_OBSERVATION, DIAGNOSTIC_SAMPLE, OFFICIAL_OCCURRENCE,
                      CONFIRMED_FOCUS, REGIONAL_STATEMENT, MODELLED_RISK,
                      OTHER_EVIDENCE)

# Estados de recusa. Recusar é um resultado, e o motivo é parte dele.
PLACE_MENTION_ONLY = 'PLACE_MENTION_NOT_FACT'
TERRITORIAL_LIST = 'TERRITORIAL_LIST_NOT_FACT'
NEGATED_OBSERVATION = 'NEGATED_OBSERVATION_NOT_FACT'

# --------------------------------------------------------------- gazetteer
# Cobertura declarada, não presumida: as 20 regiões e as províncias que o caso e
# o painel tocam. Topônimo fora daqui não vira lugar nenhum — e isso é
# NOT_IN_GAZETTEER, que não é "não é um lugar".
REGIOES = (
    'Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
    'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise',
    'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana', 'Trentino-Alto Adige',
    'Umbria', "Valle d'Aosta", 'Veneto',
)
PROVINCIAS = (
    'Grosseto', 'Siena', 'Arezzo', 'Firenze', 'Pisa', 'Livorno', 'Massa-Carrara',
    'Pistoia', 'Prato', 'Lucca', 'Foggia', 'Bari', 'Barletta-Andria-Trani',
    'Brindisi', 'Lecce', 'Taranto', 'Potenza', 'Matera', 'Palermo', 'Catania',
    'Enna', 'Caltanissetta', 'Agrigento', 'Ragusa', 'Siracusa', 'Trapani',
    'Messina', 'Bologna', 'Ferrara', 'Ravenna', 'Forli-Cesena', 'Rimini',
    'Modena', 'Parma', 'Piacenza', "Reggio nell'Emilia", 'Ancona', 'Macerata',
    'Pesaro', 'Fermo', 'Perugia', 'Terni', 'Roma', 'Viterbo', 'Latina',
    'Frosinone', 'Rieti', 'Campobasso', 'Isernia', 'Chieti', "L'Aquila",
    'Pescara', 'Teramo', 'Milano', 'Torino', 'Genova', 'Verona', 'Padova',
    # Acrescentadas em 2026-08-30 depois de ler um artigo real: "Bergamo"
    # aparecia TRÊS vezes e não era recusada por lei nenhuma — era invisível,
    # porque faltava no gazetteer. O resultado certo veio pelo motivo errado, e
    # isso não conta. As demais são a área do milho e do trigo do norte, que o
    # painel toca e o gazetteer não cobria.
    'Bergamo', 'Brescia', 'Cremona', 'Mantova', 'Pavia', 'Lodi', 'Novara',
    'Vercelli', 'Alessandria', 'Cuneo', 'Asti', 'Rovigo', 'Treviso', 'Venezia',
    'Vicenza', 'Belluno', 'Udine', 'Pordenone', 'Gorizia', 'Trieste',
)

# Um topônimo fora desta lista não é recusado: ele é INVISÍVEL. São coisas
# diferentes, e confundi-las esconde a falta de cobertura atrás de um resultado
# que parece correto. `cobertura()` existe para que a lacuna seja dizível.
#
#     NOT_IN_GAZETTEER ≠ NOT_A_PLACE ≠ REJECTED_BY_LAW
GAZETTEER = tuple([(n, REGION) for n in REGIOES] +
                  [(n, PROVINCE) for n in PROVINCIAS] +
                  [('Italia', COUNTRY), ('Italy', COUNTRY)])

# ------------------------------------------------------------------ âncoras
# Linguagem que liga ACONTECIMENTO a LUGAR. Cada uma diz também QUE espécie de
# evidência é — porque "constatata" e "campioni ricevuti" não medem a mesma coisa.
ANCORAS_POSITIVAS = (
    # O risco modelado vem PRIMEIRO: se "attacchi" fosse visto antes de "rischio
    # attacchi", um mapa de previsão viraria sintoma visto.
    (r'rischio\s+(?:di\s+)?\w+', MODELLED_RISK),
    (r'modello\s+prevision', MODELLED_RISK),
    (r'previsione\s+di\s+rischio', MODELLED_RISK),
    (r'constatat[oaie]', CONFIRMED_FOCUS),
    (r'accertat[oaie]', CONFIRMED_FOCUS),
    (r'confermat[oaie]', CONFIRMED_FOCUS),
    (r'focolai?\b', CONFIRMED_FOCUS),
    (r'osservat[oaie]', FIELD_OBSERVATION),
    (r'rilevat[oaie]', FIELD_OBSERVATION),
    (r'riscontrat[oaie]', FIELD_OBSERVATION),
    (r'sintomi\b', FIELD_OBSERVATION),
    # `attacch[io]` não pegava "attacco". Num boletim real, "lieve attacco di
    # Septoriosi nei Comuni di Branca di Gubbio" ficava sem âncora nenhuma.
    (r'attacc(?:o|hi)\b', FIELD_OBSERVATION),
    (r'presenz[ae]\s+(?:medi[ao]|alt[ao]|diffus[ao]|di)\b', FIELD_OBSERVATION),
    (r'infezion[ei]\b', FIELD_OBSERVATION),
    (r'monitoraggio\s+(?:in|nel|nella|a|ad)\b', FIELD_OBSERVATION),
    (r'campion[ei]\s+positiv[ei]', DIAGNOSTIC_SAMPLE),
    (r'campion[ei]\s+provenient[ei]', DIAGNOSTIC_SAMPLE),
    (r'analisi\s+positiv[ei]', DIAGNOSTIC_SAMPLE),
    # "si segnalano" é presente: `segnalat[oaie]` só pegava o particípio, e a
    # frase "non si segnalano infezioni" ficava sem âncora — logo, sem negação a
    # reconhecer. Recusada pelo motivo errado.
    (r'segnal(?:at[oaie]|ano|a|iamo)', OFFICIAL_OCCURRENCE),
    (r'bollettino\b', OFFICIAL_OCCURRENCE),
    (r'registrat[oaie]', OFFICIAL_OCCURRENCE),
    (r'diffusion[ei]\s+(?:in|nel|nella)\b', REGIONAL_STATEMENT),
    (r'pressione\s+(?:in|nel|nella)\b', REGIONAL_STATEMENT),
)

# Linguagem que ancora o lugar a OUTRA COISA que não o acontecimento. Cada uma
# destas foi um falso positivo medido no Brasil, traduzida para o italiano.
ANCORAS_NEGATIVAS = (
    (r'convegno\b', 'local de evento'),
    (r'event[oi]\b', 'local de evento'),
    (r'fier[ae]\b', 'local de evento'),
    (r'workshop\b', 'local de evento'),
    (r'incontro\b', 'local de evento'),
    (r'con\s+sede\b', 'endereço da entidade'),
    (r'\bsede\b', 'endereço da entidade'),
    (r'\bsedi\b', 'endereço da entidade'),
    (r'filial[ei]\b', 'endereço da entidade'),
    (r'stabilimento\b', 'endereço da entidade'),
    (r'\bufficio\b', 'endereço da entidade'),
    (r'abit[oa]\b', 'residência declarada'),
    (r'\bvivo\b', 'residência declarada'),
    (r'nat[oa]\s+a\b', 'naturalidade'),
    (r'\boperiamo\b', 'área de atuação'),
    (r'\boperiam[oa]\b', 'área de atuação'),
    (r'\battivi\b', 'área de atuação'),
    (r'serviamo\b', 'área comercial'),
    (r'\bclienti\s+(?:in|a|nel|nella)\b', 'área comercial'),
    (r'\bmercat[oi]\b', 'área econômica'),
    (r'area\s+commerciale', 'área comercial'),
    (r'zona\s+di\s+competenza', 'abrangência institucional'),
    (r'copertura\b', 'abrangência institucional'),
    (r'\bpresso\b', 'afiliação institucional'),
    (r'laurea\s+(?:a|presso)', 'formação'),
)

# O texto às vezes DECLARA o nível administrativo do lugar: "nel Comune di
# Parrano", "nei Comuni di Branca di Gubbio". Isso vale mais que o gazetteer —
# é a própria fonte dizendo o que aquele nome é. Sem isto, o boletim
# fitossanitário mais rico que encontrei devolvia ZERO localizações, porque
# comune não é província e o gazetteer só tem províncias.
#
#     DECLARED_ADMIN_MARKER > GAZETTEER
#
# O marcador dá o NÍVEL, não a permissão: o lugar continua precisando de âncora
# de acontecimento para virar FACT.
MARCADORES_ADMIN = (
    (r'comun[ei]\s+di\s+', MUNICIPALITY),
    (r'localit[àa]\s+(?:di\s+)?', LOCALITY),
    (r'frazione\s+di\s+', LOCALITY),
    (r'provincia\s+di\s+', PROVINCE),
    (r'areal[ei]\s+(?:di\s+)?', OTHER_PRECISION),
    # "testimone non trattato di Plessiva" — a parcela-sentinela. O agrônomo
    # declara ali que Plessiva é um lugar com uma parcela de monitoramento. Sem
    # este marcador, o nome ficava INVISÍVEL; com ele, passa a ser julgado — e
    # naquela frase é corretamente recusado, porque a observação está negada.
    (r'testimone(?:\s+non)?(?:\s+trattato)?\s+di\s+', LOCALITY),
    (r'(?:vigneto|campo|appezzamento|parcella)\s+di\s+', LOCALITY),
)
_NOME = r"([A-Z][\wÀ-ÿ'’-]+(?:\s+(?:di|del|della|dei|delle|d'|in)\s+[A-Z][\wÀ-ÿ'’-]+|\s+[A-Z][\wÀ-ÿ'’-]+)*)"

# Uma observação NEGADA não é uma observação. "Non riscontrata presenza di
# avversità" seguido de um topônimo produziria, sem isto, uma afirmação de que a
# doença ESTÁ ali — dizendo o oposto exato do que o boletim diz.
#
#     NEGATED_OBSERVATION ≠ OBSERVATION
# Tentar enumerar as formas verbais negadas do italiano foi um erro: a primeira
# versão listava particípios e terceira pessoa do plural, e "non si segnalano"
# não caía em nenhuma das duas. A negação é uma questão de PROXIMIDADE, não de
# morfologia — um "non" a poucas palavras da âncora nega o que ela afirma.
NEGACOES = (r'\bnon\b', r'\bassenti\b', r'\bassente\b', r'\bnessun[ao]?\b',
            r'\bnulla\b', r'\bné\b')
JANELA_NEGACAO = 40
# A negação PARA aqui: "Fitopatie assenti ad eccezione di presenza media di
# Septoriosi nel Comune di Parrano" volta a ser uma observação positiva.
FIM_DA_NEGACAO = (r'ad\s+eccezione', r'\beccetto\b', r'\btranne\b', r'\bsalvo\b',
                  r'\bfatta\s+eccezione\b')

# "testimone NON TRATTATO" não nega achado nenhum: descreve a parcela-sentinela,
# que é justamente onde a doença aparece primeiro. Tratar esse "non" como negação
# da observação faria o sistema descartar a evidência mais precoce que existe.
#
#     STRUCTURAL_NEGATION ≠ OBSERVATIONAL_NEGATION
NEGACAO_ESTRUTURAL = (
    r'(?:testimone|vigneto|campo|appezzamento|parcella|tesi)\s+non\s+trattat[oaie]',
    r'non\s+trattat[oaie]\b',
)

CONTENT_GEO_EVIDENCE = 'CONTENT_GEO_EVIDENCE'


def cobertura():
    """O que o gazetteer cobre — para que o silêncio dele seja legível.

    Sem isto, "nenhuma localização encontrada" e "nenhuma localização coberta"
    saem idênticos do outro lado.
    """
    return {'REGIONS': len(REGIOES), 'PROVINCES': len(PROVINCIAS),
            'COUNTRY_FORMS': 2, 'MUNICIPALITIES': 0,
            'LIMIT': ('só regiões, províncias e o país. Município que não seja '
                      'capoluogo de província é NOT_IN_GAZETTEER — invisível, '
                      'não recusado'),
            'ALSO_NOT_COVERED': ('zonas próprias das redes de monitoramento '
                                 '("Ovest", "areale nord") não são unidades '
                                 'administrativas e não têm entrada aqui')}


def _sem_acento(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    return ''.join(c for c in s if not unicodedata.combining(c))


def _baixo(s):
    return _sem_acento(s).lower()


def _frases(texto):
    """Quebra em orações. O governo de uma âncora não atravessa ponto final."""
    for pedaco in re.split(r'[.!?;\n\r]+', str(texto or '')):
        if pedaco.strip():
            yield pedaco.strip()


def mencoes(frase):
    """Topônimos do gazetteer nesta oração, com posição e precisão.

    Fronteira de palavra obrigatória: sem ela "Roma" casaria dentro de "Romagna"
    e "Bari" dentro de "Barletta" — substring acidental foi um dos falsos
    positivos medidos no Brasil.
    """
    low = _baixo(frase)
    fora = []
    for nome, precisao in GAZETTEER:
        # "Friuli-Venezia Giulia" e "Friuli Venezia Giulia" são o mesmo lugar, e o
        # italiano escreve das duas formas. Exigir o hífen fez a região inteira
        # não casar num boletim real — e sobrou só "Venezia", que é uma província
        # a 100 km dali. A substring voltou pela porta da grafia.
        alvo = re.escape(_baixo(nome)).replace(r'\-', '[- ]').replace(r'\ ', '[- ]')
        for m in re.finditer(r'(?<![0-9a-z])%s(?![0-9a-z])' % alvo, low):
            fora.append({'PLACE': nome, 'PRECISION': precisao, 'POS': m.start()})
    # Lugares que o PRÓPRIO TEXTO declara, com o nível que ele declara. Entram
    # mesmo sem estar no gazetteer — é a fonte nomeando a unidade, não eu.
    for padrao, precisao in MARCADORES_ADMIN:
        # O marcador é indiferente à caixa ("Comune"/"comune"); o NOME não é —
        # ele precisa vir capitalizado, senão "comune di produzione" viraria
        # lugar. Por isso a flag é escopada só no marcador.
        for m in re.finditer('(?i:%s)%s' % (padrao, _NOME), frase):
            fora.append({'PLACE': m.group(1).strip(), 'PRECISION': precisao,
                         'POS': m.start(1), 'DECLARED_BY_TEXT': True})

    # Topônimo mais longo vence no mesmo ponto: "Emilia-Romagna" antes de "Romagna".
    fora.sort(key=lambda x: (x['POS'], -len(x['PLACE'])))
    limpo, ocupado = [], []
    for m in fora:
        fim = m['POS'] + len(m['PLACE'])
        if any(m['POS'] < f and i < fim for i, f in ocupado):
            continue
        ocupado.append((m['POS'], fim))
        limpo.append(m)
    return limpo


def _ancoras(frase, padroes):
    low = _baixo(frase)
    fora = []
    for padrao, rotulo in padroes:
        for m in re.finditer(padrao, low):
            fora.append({'POS': m.start(), 'END': m.end(), 'LABEL': rotulo,
                         'TEXT': m.group(0)})
    return fora


def _negada(frase, pos_ancora):
    """A âncora positiva mais próxima está sob negação?

    Olha para trás a partir da âncora. Se houver uma negação antes dela E nenhum
    "ad eccezione di" entre as duas, a observação está negada e o lugar não é
    fato. Com a exceção pelo meio, a negação já terminou.
    """
    low = _baixo(frase)[:pos_ancora]
    # Negações estruturais saem antes de qualquer conta: elas descrevem a parcela.
    for p in NEGACAO_ESTRUTURAL:
        low = re.sub(p, 'parcella_sentinella', low)
    neg = max((m.end() for p in NEGACOES for m in re.finditer(p, low)), default=None)
    # Só nega o que está perto: um "non" no começo do parágrafo não alcança uma
    # observação trinta palavras adiante.
    if neg is None or pos_ancora - neg > JANELA_NEGACAO:
        return False
    fim = max((m.end() for p in FIM_DA_NEGACAO for m in re.finditer(p, low)), default=None)
    return fim is None or fim < neg


def _mais_perto(ancoras, pos_lugar):
    """A âncora mais próxima do lugar, ANTES ou DEPOIS dele.

    A primeira versão só olhava para trás, e o italiano põe o verbo depois do
    lugar o tempo todo: "nel testimone di Plessiva si segnalano infezioni". A
    âncora existia, vinha três palavras adiante, e o lugar era recusado por
    "falta de relação semântica" — recusado pelo motivo errado.

    Olhar para os dois lados NÃO afrouxa a regra, porque a âncora negativa
    concorre pela mesma distância: em "convegno a Bologna ... fusariosi
    constatata", "convegno" continua mais perto de Bologna que "constatata".
    """
    if not ancoras:
        return None
    return min(ancoras, key=lambda a: min(abs(a['POS'] - pos_lugar),
                                          abs(a['END'] - pos_lugar)))


def _governa(pos_lugar, positivas, negativas):
    """Qual âncora governa este lugar: a MAIS PRÓXIMA dele, dos dois lados.

    Não basta existir uma âncora positiva na oração. "Convegno a Bologna e
    fusariosi constatata a Grosseto" tem as duas, e cada lugar é governado pela
    sua. Pegar "existe positiva na frase" promoveria Bologna a foco de doença.
    """
    pos = _mais_perto(positivas, pos_lugar)
    # Quando uma âncora está DENTRO de outra, quem governa é a de fora.
    # "Rischio attacchi septoriosi" contém "attacchi": pela proximidade venceria
    # "attacchi" — e um mapa de previsão viraria sintoma visto. A âncora que
    # qualifica é a que começa antes e engloba a outra.
    if pos is not None:
        externa = [a for a in positivas
                   if a['POS'] <= pos['POS'] and a['END'] > pos['POS'] and a is not pos]
        if externa:
            pos = min(externa, key=lambda a: a['POS'])
    neg = _mais_perto(negativas, pos_lugar)
    if pos and neg:
        def d(a):
            return min(abs(a['POS'] - pos_lugar), abs(a['END'] - pos_lugar))
        return (pos, None) if d(pos) < d(neg) else (None, neg)
    return (pos, neg)


def localizacoes_do_fato(texto, *, origem='POST_TEXT'):
    """→ (aceitas, recusadas). Um conteúdo pode ter 0..N localizações do fato.

    Cada aceita traz o TRECHO que a sustenta. FACT sem trecho reproduzível não
    pode ser promovido a PROVED — é a regra que torna a afirmação auditável por
    outra pessoa, e não só por mim.
    """
    aceitas, recusadas, vistos = [], [], set()
    for frase in _frases(texto):
        ms = mencoes(frase)
        if not ms:
            continue
        positivas = _ancoras(frase, ANCORAS_POSITIVAS)
        negativas = _ancoras(frase, ANCORAS_NEGATIVAS)
        sem_ancora = [m for m in ms
                      if _governa(m['POS'], positivas, negativas)[0] is None]
        # Três ou mais topônimos numa oração sem nenhuma âncora de acontecimento
        # é lista territorial — área atendida, abrangência, roteiro de eventos.
        lista = len(sem_ancora) >= 3 and len(sem_ancora) == len(ms)
        for m in ms:
            pos, neg = _governa(m['POS'], positivas, negativas)
            if pos is not None and _negada(frase, pos['POS']):
                recusadas.append({
                    'PLACE': m['PLACE'], 'PRECISION': m['PRECISION'],
                    'STATE': NEGATED_OBSERVATION,
                    'WHY': 'a observação que ancorava este lugar está negada',
                    'EVIDENCE': frase[:300], 'ORIGIN': origem})
                continue
            chave = (m['PLACE'], m['PRECISION'])
            if pos is None:
                recusadas.append({
                    'PLACE': m['PLACE'], 'PRECISION': m['PRECISION'],
                    'STATE': TERRITORIAL_LIST if lista else PLACE_MENTION_ONLY,
                    'WHY': (neg['LABEL'] if neg else
                            'lista territorial sem âncora de acontecimento' if lista
                            else 'topônimo sem relação semântica com o acontecimento'),
                    'EVIDENCE': frase[:300], 'ORIGIN': origem})
                continue
            if chave in vistos:
                continue
            vistos.add(chave)
            aceitas.append({
                'FACT_LOCATION': m['PLACE'],
                'FACT_LOCATION_PRECISION': m['PRECISION'],
                'PRECISION_SOURCE': ('DECLARED_BY_TEXT' if m.get('DECLARED_BY_TEXT')
                                     else 'GAZETTEER'),
                'FACT_LOCATION_EVIDENCE': frase[:300],
                'FACT_LOCATION_ANCHOR': pos['TEXT'],
                'FACT_LOCATION_ORIGIN': origem,
                'TYPE_OF_EVIDENCE': pos['LABEL'],
            })
    return aceitas, recusadas


def local_declarado_do_perfil(valor, *, origem='PROFILE.location'):
    """O que o perfil declara. Candidato a BASE, e a nada mais.

    Devolver isto num campo chamado FACT_LOCATION seria a promoção mais fácil e
    mais errada de todas — e a mais tentadora, porque o campo vem preenchido.
    """
    return {
        'PLACE_KIND': BASE,
        'PROFILE_DECLARED_LOCATION': str(valor or 'NÃO SEI')[:160],
        'PROFILE_LOCATION_ORIGIN': origem,
        'PROFILE_LOCATION_PRECISION': NOT_KNOWN,
        'FACT_LOCATION': 'NOT_KNOWN',
        'WHY': 'local declarado em perfil é BASE no máximo, nunca FACT',
    }


def geo_do_conteudo(valor, *, origem='ACTOR.geo'):
    """Geotag do conteúdo. Preservada como evidência, nunca promovida a FACT.

    Geotag prova um lugar associado à publicação — de onde se postou, o que se
    marcou. Não prova onde o fenômeno agronômico ocorreu.
    """
    return {'PLACE_KIND': CONTENT_GEO_EVIDENCE, 'VALUE': str(valor or 'NÃO SEI')[:160],
            'ORIGIN': origem, 'FACT_LOCATION': 'NOT_KNOWN',
            'WHY': 'geotag não fecha localização do fato sozinha'}


# ------------------------------------------------------------------- tempo
DAY, WEEK, MONTH, SEASON, YEAR = 'DAY', 'WEEK', 'MONTH', 'SEASON', 'YEAR'
PUBLICATION_STAMP = 'PUBLICATION_STAMP_NOT_FACT_TIME'
MESES = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
         'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre')
MES_NUM = {m: i + 1 for i, m in enumerate(MESES)}

# `SEASON` vem primeiro de propósito: "stagione 2025" é sobre o ciclo da cultura,
# e um ano solto pode ser qualquer coisa — o ano da publicação, inclusive.
TEMPO = (
    (r'\b((?:campagna|annata|stagione|raccolt[oa])\s+\d{4}(?:[/-]\d{2,4})?)\b', SEASON),
    # "2025/26" é uma safra. "2011-2025" é uma SÉRIE HISTÓRICA, e foi o que este
    # padrão devolveu como tempo do fato num artigo real: quinze anos de dados
    # virando a data de um acontecimento. `_e_campanha` separa os dois.
    (r'\b(\d{4}[/-]\d{2,4})\b', SEASON),
    (r'\b(la\s+settimana\s+scorsa|questa\s+settimana|nei\s+giorni\s+scorsi)\b', WEEK),
    (r'\b(\d{1,2}\s+(?:%s)(?:\s+\d{4})?)\b' % '|'.join(MESES), DAY),
    (r'\b(oggi|ieri|stamattina)\b', DAY),
    (r'\b(?:durante|nel\s+mese\s+di|a|ad|in)\s+((?:%s))\b' % '|'.join(MESES), MONTH),
    (r'\b(?:nel|del|nella\s+stagione)\s+(\d{4})\b', YEAR),
)

# Palavras que dizem "o acontecimento se deu nesse tempo". Sem uma delas por
# perto, uma data solta no texto pode ser qualquer data — a da publicação, a de
# um congresso, a de um regulamento.
ANCORAS_DE_TEMPO_DO_FATO = (
    r'monitoraggio', r'campion[ei]', r'raccolt[oa]', r'osservat[oaie]',
    r'rilevat[oaie]', r'constatat[oaie]', r'riscontrat[oaie]', r'colpit[oaie]',
    r'contaminaz', r'superament', r'infezion', r'attacc(?:o|hi)', r'sintomi',
    r'presenz[ae]', r'fioritura', r'spigatura', r'fase\s+fenologica',
)
# `stagione`, `annata` e `campagna` saíram da lista de âncoras de propósito: elas
# aparecem DENTRO da própria expressão temporal ("annata 2021-2022"), então
# usá-las como âncora fazia toda expressão de safra se autoqualificar. Num
# boletim real isso devolveu `FACT_TIME = annata 2021` a partir da frase
# "disciplinare valido per l'annata 2021-2022" — a validade de uma norma
# entrando no campo da data do acontecimento.
#
#     REGULATORY_VALIDITY ≠ FACT_TIME
CONTEXTO_ADMINISTRATIVO = (
    r'valid[oa]\s+per', r'disciplinare', r'regolament', r'normativ',
    r'autorizzaz', r'delibera', r'decreto', r'in\s+vigore',
)


def _e_campanha(valor):
    """"2025/26" e "2025-26" são safra. "2011-2025" é intervalo de série."""
    m = re.match(r'^(\d{4})[/-](\d{2,4})$', str(valor).strip())
    if not m:
        return True                       # "stagione 2025" e afins: já é safra
    a, b = int(m.group(1)), m.group(2)
    seguinte = a + 1
    return b == str(seguinte)[-len(b):] and int(b) != 0


def _resolve_dia(texto, ano_padrao):
    """"13 febbraio [2026]" -> (2026, 2, 13). Só para comparar com a publicação."""
    m = re.match(r'(\d{1,2})\s+([a-z]+)(?:\s+(\d{4}))?$', _baixo(texto).strip())
    if not m or m.group(2) not in MES_NUM:
        return None
    ano = int(m.group(3)) if m.group(3) else ano_padrao
    return (ano, MES_NUM[m.group(2)], int(m.group(1))) if ano else None


def tempo_do_fato(texto, published_at=None):
    """FACT_TIME só com evidência própria. `published_at` NUNCA o preenche.

    A primeira versão pegava a PRIMEIRA expressão temporal do texto. Num artigo
    de imprensa, a primeira expressão é o carimbo da publicação — e ela devolvia,
    para uma reportagem de 13/02/2026 sobre a safra de 2025, `FACT_TIME =
    13 febbraio`. Ou seja: entregava a data de publicação no campo que existe
    exatamente para não recebê-la. A lei estava escrita e a implementação a
    contornava por dentro.

        PUBLISHED_AT ≠ FACT_TIME

    Agora: toda expressão temporal é candidata; a que RESOLVE para a data de
    publicação é descartada como `PUBLICATION_STAMP`; e vence a que estiver
    amarrada ao acontecimento — por ser de safra/estação, ou por dividir a
    oração com uma âncora de tempo do fato. Sem nenhuma assim, o resultado é
    `NOT_KNOWN` com os candidatos à vista, e não um chute com cara de precisão.
    """
    ano_pub = None
    if published_at and re.match(r'^\d{4}-\d{2}-\d{2}$', str(published_at)):
        ano_pub = int(str(published_at)[:4])
    pub = tuple(int(x) for x in str(published_at).split('-')) if ano_pub else None

    candidatos, descartados = [], []
    for frase in _frases(texto):
        low = _baixo(frase)
        if any(re.search(a, low) for a in CONTEXTO_ADMINISTRATIVO):
            # A oração fala da validade de uma norma, não de um acontecimento.
            for padrao, _ in TEMPO:
                for m in re.finditer(padrao, low):
                    descartados.append({'VALUE': m.group(1),
                                        'WHY': 'REGULATORY_VALIDITY_NOT_FACT_TIME'})
            continue
        ancorada = any(re.search(a, low) for a in ANCORAS_DE_TEMPO_DO_FATO)
        for padrao, precisao in TEMPO:
            for m in re.finditer(padrao, low):
                valor = m.group(1)
                if precisao == DAY and pub and _resolve_dia(valor, ano_pub) == pub:
                    descartados.append({'VALUE': valor, 'WHY': PUBLICATION_STAMP})
                    continue
                if precisao == SEASON and not _e_campanha(valor):
                    # Intervalo de série histórica: é o alcance da MEDIÇÃO, não a
                    # data do que foi medido. Fica registrado, não vira FACT_TIME.
                    descartados.append({'VALUE': valor, 'WHY': 'SERIES_RANGE_NOT_FACT_TIME'})
                    continue
                candidatos.append({
                    'VALUE': valor, 'PRECISION': precisao,
                    'TIED_TO_EVENT': ancorada,
                    'EVIDENCE': frase[:220]})

    def peso(c):
        # Safra/estação primeiro: é a única que fala do ciclo da cultura por si.
        return (0 if c['PRECISION'] == SEASON and c['TIED_TO_EVENT'] else
                1 if c['TIED_TO_EVENT'] else 2)

    amarrados = [c for c in candidatos if c['TIED_TO_EVENT']]
    if amarrados:
        e = sorted(amarrados, key=peso)[0]
        return {'FACT_TIME': e['VALUE'], 'FACT_TIME_PRECISION': e['PRECISION'],
                'FACT_TIME_EVIDENCE': e['EVIDENCE'],
                'FACT_TIME_ORIGIN': 'TEXT/TIED_TO_EVENT',
                'PUBLISHED_AT': published_at or 'NOT_DATED_PRECISELY',
                'TIME_CANDIDATES_DISCARDED': descartados}
    return {'FACT_TIME': 'NOT_KNOWN', 'FACT_TIME_PRECISION': NOT_KNOWN,
            'FACT_TIME_EVIDENCE': None, 'FACT_TIME_ORIGIN': 'NOT_STATED',
            'PUBLISHED_AT': published_at or 'NOT_DATED_PRECISELY',
            'FACT_TIME_CANDIDATES': [c['VALUE'] for c in candidatos][:8],
            'TIME_CANDIDATES_DISCARDED': descartados,
            'WHY': ('nenhuma expressão temporal ficou amarrada ao acontecimento; '
                    'a data de publicação não preenche esse campo')}


def ocorrencia_nao_e_incidencia(tipos):
    """As espécies de evidência não se somam. Devolve a contagem POR espécie.

    Somar tudo produziria um número que parece medida de pressão regional e não
    é: cinco amostras de diagnóstico e um comunicado regional não fazem "seis
    ocorrências". Nem fazem incidência nenhuma.
    """
    por_tipo = {t: 0 for t in TIPOS_DE_EVIDENCIA}
    for t in tipos:
        por_tipo[t if t in por_tipo else OTHER_EVIDENCE] += 1
    return {
        'BY_TYPE_OF_EVIDENCE': {k: v for k, v in por_tipo.items() if v},
        # Risco modelado e comunicado regional ficam FORA da contagem de
        # ocorrências observadas. Somá-los faria uma previsão virar um caso.
        'OBSERVED_OCCURRENCES': sum(por_tipo[t] for t in
                                    (FIELD_OBSERVATION, DIAGNOSTIC_SAMPLE,
                                     OFFICIAL_OCCURRENCE, CONFIRMED_FOCUS)),
        'MODELLED_RISK_STATEMENTS': por_tipo[MODELLED_RISK],
        'INCIDENCE': 'NOT_KNOWN',
        'PREVALENCE': 'NOT_KNOWN',
        'REGIONAL_PRESSURE': 'NOT_KNOWN',
        'WHY': ('ocorrência observada não é incidência, prevalência nem pressão '
                'regional — e as espécies de evidência não se somam entre si'),
    }


if __name__ == '__main__':
    exemplo = ('Convegno a Bologna sulla difesa. Fusariosi constatata a Grosseto '
               'la settimana scorsa. Operiamo in Toscana e Umbria.')
    ok, nao = localizacoes_do_fato(exemplo)
    for a in ok:
        print('FACT  ', a['FACT_LOCATION'], a['FACT_LOCATION_PRECISION'],
              a['TYPE_OF_EVIDENCE'], '|', a['FACT_LOCATION_ANCHOR'])
    for r in nao:
        print('RECUSA', r['PLACE'], r['STATE'], '|', r['WHY'])
    print(tempo_do_fato(exemplo, '2026-04-20'))
