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
OTHER_EVIDENCE = 'OTHER'
TIPOS_DE_EVIDENCIA = (FIELD_OBSERVATION, DIAGNOSTIC_SAMPLE, OFFICIAL_OCCURRENCE,
                      CONFIRMED_FOCUS, REGIONAL_STATEMENT, OTHER_EVIDENCE)

# Estados de recusa. Recusar é um resultado, e o motivo é parte dele.
PLACE_MENTION_ONLY = 'PLACE_MENTION_NOT_FACT'
TERRITORIAL_LIST = 'TERRITORIAL_LIST_NOT_FACT'

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
)

GAZETTEER = tuple([(n, REGION) for n in REGIOES] +
                  [(n, PROVINCE) for n in PROVINCIAS] +
                  [('Italia', COUNTRY), ('Italy', COUNTRY)])

# ------------------------------------------------------------------ âncoras
# Linguagem que liga ACONTECIMENTO a LUGAR. Cada uma diz também QUE espécie de
# evidência é — porque "constatata" e "campioni ricevuti" não medem a mesma coisa.
ANCORAS_POSITIVAS = (
    (r'constatat[oaie]', CONFIRMED_FOCUS),
    (r'accertat[oaie]', CONFIRMED_FOCUS),
    (r'confermat[oaie]', CONFIRMED_FOCUS),
    (r'focolai?\b', CONFIRMED_FOCUS),
    (r'osservat[oaie]', FIELD_OBSERVATION),
    (r'rilevat[oaie]', FIELD_OBSERVATION),
    (r'riscontrat[oaie]', FIELD_OBSERVATION),
    (r'sintomi\b', FIELD_OBSERVATION),
    (r'attacch[io]\b', FIELD_OBSERVATION),
    (r'infezion[ei]\b', FIELD_OBSERVATION),
    (r'monitoraggio\s+(?:in|nel|nella|a|ad)\b', FIELD_OBSERVATION),
    (r'campion[ei]\s+positiv[ei]', DIAGNOSTIC_SAMPLE),
    (r'campion[ei]\s+provenient[ei]', DIAGNOSTIC_SAMPLE),
    (r'analisi\s+positiv[ei]', DIAGNOSTIC_SAMPLE),
    (r'segnalat[oaie]', OFFICIAL_OCCURRENCE),
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

CONTENT_GEO_EVIDENCE = 'CONTENT_GEO_EVIDENCE'


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
        alvo = _baixo(nome)
        for m in re.finditer(r'(?<![0-9a-z])%s(?![0-9a-z])' % re.escape(alvo), low):
            fora.append({'PLACE': nome, 'PRECISION': precisao, 'POS': m.start()})
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
            fora.append({'POS': m.start(), 'LABEL': rotulo, 'TEXT': m.group(0)})
    return fora


def _governa(pos_lugar, positivas, negativas):
    """Qual âncora governa este lugar: a MAIS PRÓXIMA antes dele.

    Não basta existir uma âncora positiva na oração. "Convegno a Bologna e
    fusariosi constatata a Grosseto" tem as duas, e cada lugar é governado pela
    sua. Pegar "existe positiva na frase" promoveria Bologna a foco de doença.
    """
    pos = max((a for a in positivas if a['POS'] < pos_lugar),
              key=lambda a: a['POS'], default=None)
    neg = max((a for a in negativas if a['POS'] < pos_lugar),
              key=lambda a: a['POS'], default=None)
    if pos and neg:
        return (pos, None) if pos['POS'] > neg['POS'] else (None, neg)
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
MESES = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
         'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre')
TEMPO = (
    (r'\b(\d{4}-\d{2}-\d{2})\b', DAY),
    (r'\b(\d{1,2}\s+(?:%s))\b' % '|'.join(MESES), DAY),
    (r'\b(oggi|ieri|stamattina)\b', DAY),
    (r'\b(la\s+settimana\s+scorsa|questa\s+settimana|nei\s+giorni\s+scorsi)\b', WEEK),
    (r'\b(?:durante|a|ad|nel\s+mese\s+di|in)\s+((?:%s))\b' % '|'.join(MESES), MONTH),
    (r'\b(campagna\s+\d{4}[/-]\d{2,4}|annata\s+\d{4}[/-]\d{2,4})\b', SEASON),
    (r'\b(\d{4}[/-]\d{2,4})\b', SEASON),
    (r'\b(?:nel|del)\s+(\d{4})\b', YEAR),
)


def tempo_do_fato(texto, published_at=None):
    """FACT_TIME só com evidência própria. `published_at` NUNCA o preenche.

    Um post de 20/04 que diz "la settimana scorsa" fala de meados de abril; um
    que diz "campagna 2025/26" fala de uma safra inteira. Copiar a data de
    publicação para dentro do fato inventaria precisão que ninguém declarou.

        PUBLISHED_AT ≠ FACT_TIME
    """
    low = _baixo(texto)
    for padrao, precisao in TEMPO:
        m = re.search(padrao, low)
        if m:
            return {'FACT_TIME': m.group(1), 'FACT_TIME_PRECISION': precisao,
                    'FACT_TIME_EVIDENCE': texto[max(0, m.start() - 60):m.end() + 60],
                    'FACT_TIME_ORIGIN': 'POST_TEXT',
                    'PUBLISHED_AT': published_at or 'NOT_DATED_PRECISELY'}
    return {'FACT_TIME': 'NOT_KNOWN', 'FACT_TIME_PRECISION': NOT_KNOWN,
            'FACT_TIME_EVIDENCE': None, 'FACT_TIME_ORIGIN': 'NOT_STATED',
            'PUBLISHED_AT': published_at or 'NOT_DATED_PRECISELY',
            'WHY': 'o texto não datou o acontecimento; a data de publicação não '
                   'preenche esse campo'}


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
        'OBSERVED_OCCURRENCES': sum(por_tipo[t] for t in
                                    (FIELD_OBSERVATION, DIAGNOSTIC_SAMPLE,
                                     OFFICIAL_OCCURRENCE, CONFIRMED_FOCUS)),
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
