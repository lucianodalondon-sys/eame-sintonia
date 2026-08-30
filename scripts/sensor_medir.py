#!/usr/bin/env python3
"""
MEDIÇÃO DO PILOTO — classifica e consolida, de graça, o que já foi pago.

    python3 scripts/sensor_medir.py

POR QUE A MEDIÇÃO É SEPARADA DA COLETA
---------------------------------------
Classificador erra. Este errou duas vezes já nesta missão, e as duas vezes o conserto foi
de graça porque a classificação nunca esteve dentro da execução paga. Se estivesse, cada
correção de régua custaria uma coleta nova.

    RAW -> NORMALIZED -> ANALYTICAL, e a terceira seta é reexecutável.

O LIMITE DESTE CLASSIFICADOR, DECLARADO ANTES DO NÚMERO
---------------------------------------------------------
Ele é LEXICAL. A casa já mediu o que isso custa: `El repilo del olivo **en acción**` virou
`PRODUCT_DEMO`, e `**Curso** natural del agua` virou `TECHNICAL_WEBINAR`. Polissemia
produz falso positivo e **nenhum portão automático detecta isso**.

Por isso todo item carrega `CONTENT_TYPE_EVIDENCE` com o termo que decidiu, e a
verificação de verdade é humana. Cobertura alta aqui é suspeita, não conquista.

O QUE NÃO SE INFERE, NUNCA
---------------------------
`COUNTRY_OF_FACT` só sai quando o texto NOMEIA o lugar. Idioma não é lugar: a busca
espanhola devolveu vídeo italiano da Accademia dei Georgofili e vídeo uruguaio da
Agrociencia. Nacionalidade da pessoa também não é lugar do fato.

    COUNTRY_OF_PERSON != COUNTRY_OF_FACT. IDIOMA != LUGAR.
"""
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
PILOT = os.path.join(SAMPLES, 'SENSOR-PILOT')

NAO_SEI = 'NOT_KNOWN'


def _n(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def _ler(nome):
    caminho = os.path.join(PILOT, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# ── LÉXICOS DECLARADOS ───────────────────────────────────────────────────────────
# Cada termo é uma aposta explícita e auditável. Multilíngue porque o corpus é.
OBSERVACAO_CAMPO = [
    'hemos observado', 'se ha detectado', 'hemos detectado', 'en campo hemos',
    'abbiamo osservato', 'abbiamo rilevato', 'in campo abbiamo', 'si e osservato',
    'nous avons observe', 'on a observe', 'nous avons constate', 'au champ',
    'observamos', 'detectamos', 'primeros sintomas', 'primi sintomi',
    'premiers symptomes', 'este ano hemos', "quest'anno abbiamo", 'cette annee',
]
PESQUISA = [
    'nuestro estudio', 'nuestros resultados', 'el ensayo', 'los ensayos',
    'nostro studio', 'i nostri risultati', 'la prova', 'le prove sperimentali',
    'notre etude', 'nos resultats', 'essai', 'experimental', 'ensayo de campo',
    'resultados del ensayo', 'publicamos', 'abbiamo pubblicato',
]
INTERPRETACAO = [
    'esto significa', 'esto se debe', 'la razon es', 'por lo tanto',
    'questo significa', 'questo e dovuto', 'quindi', 'percio',
    'cela signifie', 'cela est du', 'donc', 'par consequent', 'recomendamos',
    'raccomandiamo', 'nous recommandons', 'se recomienda', 'si consiglia',
]
EVENTO = ['jornada', 'congreso', 'convegno', 'giornata', 'colloque', 'journee',
          'webinar', 'webinaire', 'seminario', 'inscripcion', 'iscrizione',
          'inscription', 'programa del', 'programma del']
MARKETING = ['nuestro producto', 'compra', 'disponible en tienda', 'oferta',
             'nostro prodotto', 'acquista', 'notre produit', 'achetez',
             'suscribete', 'iscriviti', 'abonnez-vous', 'suscríbete']
NOTICIA = ['segun informa', 'fuente:', 'redaccion', 'secondo quanto', 'fonte:',
           "d'apres", 'source :', 'comunicado de prensa', 'comunicato stampa']

# Comentário em primeira pessoa sobre a própria lavoura. É o que o subexperimento procura.
PRIMEIRA_PESSOA = [
    'en mi finca', 'en mi olivar', 'en mi parcela', 'mis olivos', 'mi cultivo',
    'aqui en mi', 'tengo el problema', 'me paso', 'nos paso', 'aplicamos',
    'he aplicado', 'hemos aplicado', 'no me funciono', 'no funciono',
    # `i miei` sozinho casava "i miei genitori" e "i miei baby 520". Posse sem objeto
    # nomeado não é relato de lavoura.
    'nel mio campo', 'nel mio vigneto', 'nella mia azienda', 'i miei vitigni',
    'i miei olivi', 'i miei vigneti', 'la mia azienda', 'il mio vigneto',
    'ho applicato', 'abbiamo applicato', 'non ha funzionato',
    'dans ma parcelle', 'dans mon vignoble', 'chez moi', "j'ai applique",
    'nous avons applique', 'ca n a pas marche',
]
SEGUNDA_MAO = ['un vecino', 'un amigo', 'me dijeron', 'dicen que', 'un vicino',
               'mi hanno detto', 'dicono che', 'un voisin', 'on m a dit']
PERGUNTA = ['?', 'como puedo', 'que puedo', 'alguien sabe', 'come posso',
            'que tratamiento', 'que producto', 'cuando aplicar', 'che trattamento',
            'quale prodotto', 'quel traitement', 'quel produit', 'debo aplicar',
            'qualcuno sa', 'comment', 'quelqu un sait']
RUIDO = ['gracias', 'grazie', 'merci', 'buen video', 'bel video', 'super',
         'excelente', 'eccellente', 'bravo', 'felicidades', 'complimenti']

# Lugares NOMEADOS. Lista fechada e por país — é declaração, não dicionário aberto.
#
# DUAS COISAS APRENDIDAS LENDO OS RESULTADOS, E AS DUAS ESTÃO CORRIGIDAS AQUI:
#
# 1. `marche` (a região italiana) casou dentro de um comentário FRANCÊS — "ça marche".
#    Um comentário de trigo francês saiu com COUNTRY_OF_FACT = IT. É o mesmo bug de
#    token curto que já custou uma classificação inteira nesta casa. Termos que são
#    palavra comum em outra língua do corpus saem da lista ou ganham qualificador.
# 2. `Trentino` não estava aqui, e o melhor relato de campo de toda a coleta — um
#    viticultor dizendo que sua propriedade foi destruída pela flavescência — ficou com
#    lugar NOT_KNOWN por causa da MINHA lista, não da fonte.
#
#     LISTA CURTA NÃO É AUSÊNCIA DE LUGAR. É AUSÊNCIA NA MINHA LISTA.
LUGARES = {
    'ES': ['espana', 'andalucia', 'cordoba', 'jaen', 'sevilla', 'granada', 'huelva',
           'cadiz', 'aragon', 'catalunya', 'cataluna', 'extremadura', 'castilla',
           'navarra', 'murcia', 'toledo', 'badajoz', 'la rioja', 'galicia'],
    'IT': ['italia', 'veneto', 'lombardia', 'piemonte', 'puglia', 'emilia',
           'toscana', 'umbria', 'friuli', 'sicilia', 'sardegna', 'trentino',
           'alto adige', 'campania', 'abruzzo', 'foggia', 'verona', 'treviso',
           'conegliano', 'valpolicella', 'chianti', 'le marche', 'regione marche'],
    'FR': ['france', 'bordeaux', 'bourgogne', 'champagne', 'occitanie', 'aquitaine',
           'beaujolais', 'alsace', 'gironde', 'charente', 'bretagne', 'normandie',
           'picardie', 'beauce', 'val de loire', 'cotes du rhone', 'languedoc'],
}


def _tem(texto, termos):
    for t in termos:
        if _n(t) in texto:
            return t
    return None


def classificar_conteudo(titulo, descricao, transcricao):
    """→ (tipo, evidência). Sem texto suficiente NÃO vira OTHER: vira NOT_ENOUGH_TEXT."""
    corpo = _n('%s %s' % (descricao or '', transcricao or ''))
    tit = _n(titulo)
    # Sem corpo, o título sozinho não promove nada a sinal técnico. É a lição do Xylella:
    # descrição sozinha não é conteúdo técnico.
    if len(corpo.strip()) < 200:
        return 'NOT_ENOUGH_TEXT', (
            'só %d caracteres de descrição/transcrição. Título não vira observação '
            'técnica sozinho.' % len(corpo.strip()))
    for tipo, lex in (('MARKETING', MARKETING), ('NEWS_REPOST', NOTICIA),
                      ('FIELD_OBSERVATION', OBSERVACAO_CAMPO),
                      ('RESEARCH_COMMUNICATION', PESQUISA),
                      ('TECHNICAL_INTERPRETATION', INTERPRETACAO)):
        achou = _tem(corpo, lex)
        if achou:
            return tipo, 'termo "%s" no corpo do texto' % achou
    achou = _tem(tit + ' ' + corpo, EVENTO)
    if achou:
        return 'EVENT_PROMOTION', 'termo "%s"' % achou
    return 'NOISE', 'nenhum marcador dos léxicos declarados apareceu'


def classificar_comentario(texto):
    """A ORDEM foi corrigida depois de ler os 13 primeiros resultados, um a um.

    Três erros apareceram na leitura, e os três eram de ordem ou de léxico:

    1. **Pergunta vinha depois de primeira pessoa.** *"Que tratamiento para mis olivos"* e
       *"he visto repilo en mi olivar... debo aplicar?"* saíam como RELATO DE CAMPO. São
       perguntas — e o acervo espanhol já mediu que o comentário de YouTube no olivar
       mede DEMANDA POR INFORMAÇÃO, não estado do campo. Ler pergunta como resposta é
       exatamente o erro que aquela medição existe para impedir.
    2. **`i miei` era genérico demais.** Ele casou *"i miei genitori"* (meus pais) e
       *"I miei baby 520 vanno alla grande"* — conversa, não lavoura. O dono do canal
       respondendo aos seguidores virou três relatos de campo.
    3. Um marcador de posse não diz de QUE se possui. Agora os termos italianos nomeiam a
       coisa: `i miei vitigni`, `i miei olivi`, `la mia azienda`.
    """
    t = _n(texto)
    if len(t.strip()) < 12:
        return 'NOISE', 'texto com menos de 12 caracteres'
    # PERGUNTA PRIMEIRO. Quem pergunta não está relatando.
    if _tem(t, PERGUNTA):
        return 'QUESTION', 'marcador de pergunta — e pergunta não é relato'
    achou = _tem(t, PRIMEIRA_PESSOA)
    if achou:
        return 'FIRST_PERSON_FIELD_REPORT', 'termo "%s"' % achou
    achou = _tem(t, SEGUNDA_MAO)
    if achou:
        return 'SECOND_HAND_FIELD_REPORT', 'termo "%s"' % achou
    achou = _tem(t, MARKETING)
    if achou:
        return 'MARKETING', 'termo "%s"' % achou
    achou = _tem(t, INTERPRETACAO + PESQUISA)
    if achou:
        return 'TECHNICAL_REPLY', 'termo "%s"' % achou
    if _tem(t, RUIDO) and len(t) < 80:
        return 'NOISE', 'agradecimento/elogio curto'
    return 'OPINION', 'texto com conteúdo, sem marcador de campo nem de técnica'


def lugar_do_fato(texto):
    """Só quando o texto NOMEIA. Idioma não é lugar."""
    t = _n(texto)
    for pais, nomes in LUGARES.items():
        achou = _tem(t, nomes)
        if achou:
            return pais, achou
    return NAO_SEI, None


def medir():
    videos, vistos = [], set()
    trans = {}
    for L in ('A', 'B'):
        d = _ler('TRANSCRICOES-%s.json' % L) or {'ITEMS': []}
        for t in d['ITEMS']:
            if t.get('TRANSCRIPT'):
                trans[t['SOURCE_URL']] = t['TRANSCRIPT']
    dups = 0
    for L in ('A', 'B'):
        d = _ler('VIDEOS-%s.json' % L) or {'ITEMS': []}
        for v in d['ITEMS']:
            chave = ('YOUTUBE', v.get('EXTERNAL_ID'))
            if chave in vistos:                      # DEDUPE GLOBAL entre lotes
                dups += 1
                continue
            vistos.add(chave)
            tr = trans.get(v['SOURCE_URL'])
            tipo, ev = classificar_conteudo(v.get('TITLE'), v.get('DESCRIPTION'), tr)
            pais_fato, nome = lugar_do_fato(
                '%s %s %s' % (v.get('TITLE'), v.get('DESCRIPTION'), tr or ''))
            videos.append(dict(v, **{
                'CONTENT_TYPE': tipo, 'CONTENT_TYPE_EVIDENCE': ev,
                'TRANSCRIPT_AVAILABLE': 'YES' if tr else 'NO',
                'TRANSCRIPT_CHARS': len(tr or ''),
                'COUNTRY_OF_FACT': pais_fato,
                'COUNTRY_OF_FACT_EVIDENCE': ('o texto nomeia "%s"' % nome) if nome
                else 'nenhum lugar nomeado no texto — idioma não é lugar',
            }))

    # RECOSTURA, de graça, do que a normalização da coleta perdeu.
    # O ator de comentários não devolve `videoUrl` — devolve `videoId`. Meu join na hora
    # da coleta procurou pela URL e não achou, então CASE_ID, CROP, ISSUE e SOURCE_ENTITY
    # saíram NÃO SEI em 991 comentários. O dado nunca se perdeu: `VIDEO_ID` está em todos.
    # Refazer o join aqui custa zero; refazer a coleta custaria as 991 linhas de novo.
    por_id = {v.get('EXTERNAL_ID'): v for v in videos}

    coments, vistos_c, dups_c = [], set(), 0
    for L in ('A', 'B'):
        d = _ler('COMENTARIOS-%s.json' % L) or {'ITEMS': []}
        for c in d['ITEMS']:
            chave = c.get('COMMENT_ID')
            if chave and chave in vistos_c:
                dups_c += 1
                continue
            vistos_c.add(chave)
            v = por_id.get(c.get('VIDEO_ID')) or {}
            c = dict(c, **{
                'CASE_ID': v.get('CASE_ID', c.get('CASE_ID')),
                'CROP': v.get('CROP', c.get('CROP')),
                'ISSUE': v.get('ISSUE', c.get('ISSUE')),
                'SOURCE_ENTITY': v.get('SOURCE_ENTITY', c.get('SOURCE_ENTITY')),
                'SOURCE_URL': v.get('SOURCE_URL', c.get('SOURCE_URL')),
                'VIDEO_TITLE': v.get('TITLE', NAO_SEI),
                # O ator dá o HANDLE, não um id de conta. Handle é o que existe, e é o que
                # separa uma testemunha de outra — mas ele NÃO é pessoa, e por isso todo
                # autor continua UNVERIFIED. É a mesma lei que já vale no acervo espanhol.
                'COMMENTER_KEY': c.get('COMMENTER_NAME') or NAO_SEI,
                'COMMENTER_KEY_BASIS': 'handle público; HANDLE != PESSOA',
            })
            tipo, ev = classificar_comentario(c.get('COMMENT_TEXT_RAW'))
            pais_fato, nome = lugar_do_fato(c.get('COMMENT_TEXT_RAW'))
            coments.append(dict(c, **{
                'SPEECH_TYPE': tipo, 'SPEECH_TYPE_EVIDENCE': ev,
                'COUNTRY_OF_FACT': pais_fato,
                'COUNTRY_OF_FACT_EVIDENCE': ('o texto nomeia "%s"' % nome) if nome
                else 'nenhum lugar nomeado',
                # Voz observada NUNCA é problema confirmado.
                'FIELD_STATE': ('FIELD_VOICE_OBSERVED'
                                if tipo in ('FIRST_PERSON_FIELD_REPORT',
                                            'SECOND_HAND_FIELD_REPORT')
                                else 'NOT_A_FIELD_REPORT'),
            }))
    return videos, coments, dups, dups_c


if __name__ == '__main__':
    videos, coments, dups, dups_c = medir()
    canal = _ler('CANAL-IDENTIDADE.json') or {'ITEMS': []}

    def conta(itens, chave):
        r = {}
        for i in itens:
            r[i[chave]] = r.get(i[chave], 0) + 1
        return dict(sorted(r.items(), key=lambda kv: -kv[1]))

    tipos = conta(videos, 'CONTENT_TYPE')
    fala = conta(coments, 'SPEECH_TYPE')
    com_tr = sum(1 for v in videos if v['TRANSCRIPT_AVAILABLE'] == 'YES')
    com_pais = sum(1 for v in videos if v['COUNTRY_OF_FACT'] != NAO_SEI)
    relevantes = [v for v in videos if v['CONTENT_TYPE'] in
                  ('FIELD_OBSERVATION', 'RESEARCH_COMMUNICATION',
                   'TECHNICAL_INTERPRETATION')]
    entidades = {}
    for v in videos:
        entidades.setdefault(v.get('CASE_ID'), set()).add(v.get('SOURCE_ENTITY'))
    autores = {}
    for c in coments:
        if c['FIELD_STATE'] == 'FIELD_VOICE_OBSERVED':
            autores.setdefault(c.get('CASE_ID'), set()).add(c.get('COMMENTER_KEY'))

    corpo = {
        'SOURCE_ID': 'SENSOR-PILOT/MEDICAO',
        'source': 'derivado do material já coletado — nenhuma execução nova',
        'SOURCE_LOCATION': 'derivado', 'FACT_LOCATION': 'ver por item',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'LIMITE_DO_CLASSIFICADOR': (
            'lexical. Polissemia produz falso positivo e nenhum portão automático detecta '
            'isso. Todo item carrega CONTENT_TYPE_EVIDENCE; a verificação é humana.'),
        'VIDEOS': len(videos), 'VIDEOS_DUPLICADOS_INTERCEPTADOS': dups,
        'VIDEOS_POR_TIPO': tipos,
        'TRANSCRIPTS_AVAILABLE': com_tr,
        'TRANSCRIPT_CHARS': sum(v['TRANSCRIPT_CHARS'] for v in videos),
        'VIDEOS_COM_COUNTRY_OF_FACT': com_pais,
        'TECHNICAL_RELEVANT_ITEMS': len(relevantes),
        'COMMENTS': len(coments), 'COMMENTS_DUPLICADOS_INTERCEPTADOS': dups_c,
        'COMMENTS_POR_TIPO': fala,
        'UNIQUE_COMMENTERS': len({c.get('COMMENTER_KEY') for c in coments} - {NAO_SEI}),
        'FIELD_VOICE_OBSERVED': sum(1 for c in coments
                                    if c['FIELD_STATE'] == 'FIELD_VOICE_OBSERVED'),
        'COMMENTS_COM_COUNTRY_OF_FACT': sum(1 for c in coments
                                            if c['COUNTRY_OF_FACT'] != NAO_SEI),
        'SOURCE_ENTITIES_POR_RECORTE': {k: len(v) for k, v in sorted(entidades.items())},
        'FIELD_VOICES_POR_RECORTE': {k: len(v) for k, v in sorted(autores.items())},
        'CHANNEL_IDENTITY': canal.get('BY_STATE'),
        'VIDEOS_ITEMS': videos, 'COMMENTS_ITEMS': coments,
    }
    with open(os.path.join(PILOT, 'MEDICAO.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('VIDEOS %d (dup interceptadas %d) · transcritos %d · com lugar nomeado %d'
          % (len(videos), dups, com_tr, com_pais))
    print('  tipos:', tipos)
    print('COMENTARIOS %d (dup %d) · autores unicos %d'
          % (len(coments), dups_c, corpo['UNIQUE_COMMENTERS']))
    print('  tipos:', fala)
    print('  FIELD_VOICE_OBSERVED:', corpo['FIELD_VOICE_OBSERVED'])
    print('entidades distintas por recorte:', corpo['SOURCE_ENTITIES_POR_RECORTE'])
