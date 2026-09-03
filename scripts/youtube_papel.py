#!/usr/bin/env python3
"""
QUEM É TÉCNICO? — o papel que o canal DECLARA de si, e o que isso não prova.

    py scripts/youtube_papel.py medir     # classifica os canais italianos
    py scripts/youtube_papel.py teste     # as provas, sem rede

⚠️ ISTO NÃO PRODUZ `DECLARED_ROLE`, E A DIFERENÇA É O ARQUIVO INTEIRO
=======================================================================
A regra de papel desta casa está escrita em `ES-VOICE-LINKEDIN.json`:

    ROLE_RULE.PAGE      companyType + pageType + industries (CAMPOS ESTRUTURADOS)
    ROLE_RULE.PERSON    headline + cargo atual DECLARADOS
    ROLE_RULE.NAO_USADO ['nome da conta', 'foto', 'estilo do texto', 'idioma',
                         'PROSA LIVRE (about/description)']

E o porquê, com três erros já medidos: *"na prosa aparecem terceiros citados
('Junta de Andalucia'), palavras de notícia ('investigador') e nomes químicos que
contêm tokens de instituto (`ftalimida` contém `imida`)"*.

**No YouTube só existe prosa livre.** Não há `companyType`, não há `headline`, não
há cargo estruturado. Então este arquivo produz `ROLE_CANDIDATE_FROM_PROSE`, que é
um estado MAIS FRACO e tem nome diferente de propósito:

    PROSA NÃO DECIDE PAPEL. ELA INDICA ONDE PERGUNTAR.

A promoção de candidato a `DECLARED_ROLE` exige fonte estruturada — LinkedIn com
`Full`, ou o registro profissional (CONAF, Collegio dei Periti Agrari, Agrotecnici),
que é o único lugar onde "dottore agronomo" é campo declarado por lei.

O QUE FOI MEDIDO NESTE CORPUS EM 2026-09-03
==============================================
168 canais italianos com descrição, dos 226 do recorte.

1. **Fronteira de palavra: ZERO falsos aqui.** `agronom` casou 16 vezes com e sem
   fronteira; `tecnic`, 23 com e sem. O guarda continua ligado — ele é profilático,
   e dizer que ele consertou algo neste corpus seria inventar um mérito. Mas
   `zootecnico` contém `tecnic`, e basta um canal de zootecnia entrar para o guarda
   passar a valer.

2. **O erro REAL não é de substring, é de sentido.** `Orto Da Coltivare` tem
   `agronom`, `tecnic` E `divulgaz` na descrição — e é canal de HORTA DOMÉSTICA:
   *"consigli su come coltivare orto e frutteto con metodo biologico"*. Nenhuma
   regra de fronteira pega isso.

       O CANAL QUE CITA UM AGRÔNOMO NÃO É UM AGRÔNOMO.

   Por isso todo achado carrega o TRECHO LITERAL, e por isso o conflito com a
   plateia é um campo publicado e não um desempate silencioso.

3. **O acerto que justifica a rota**: `Agralia studio di agronomia` —
   *"Agralia è un team di Dottori Agronomi che offrono servizi alle aziende
   agricole"*. E `Sata S.r.l.` — *"SATA è una società di agronomi"*. Os dois estavam
   entre os 361 canais que ninguém tinha triado.

O LÉXICO É UMA APOSTA DECLARADA, E NÃO ESTAVA EM LUGAR NENHUM
================================================================
Nenhum arquivo desta casa tinha vocabulário de cargo italiano. Este é o primeiro,
e por isso cada raiz abaixo vale o que vale: uma lista escrita à mão, conferível
contra o corpus e corrigível. As contagens ao lado são do corpus REAL — raiz com
contagem zero é palpite meu, e está marcada como tal na saída.
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
JANELA = os.path.join(SAMPLES, 'YOUTUBE-JANELA')
RELEV = os.path.join(SAMPLES, 'YOUTUBE-RELEVANCIA')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-PAPEL')
NAO_SEI = 'NOT_KNOWN'
MISSION = '17-PAPEL-DECLARADO-ITALIA'

# ── O LÉXICO DE CARGO ITALIANO ────────────────────────────────────────────────
# Os estados são os de `ES-VOICE-LINKEDIN.json::ROLE_BY_ORIGIN`, herdados e não
# reinventados, para que uma lista espanhola e uma italiana possam ser somadas.
RAIZES = {
    # pessoa técnica que aconselha — o alvo desta missão
    'TECHNICAL_ADVISER': ['agronom', 'perito agrar', 'agrotecnic', 'consulent',
                          'assistenza tecnic', 'tecnico di zona', 'fitopatolog',
                          'entomolog', 'enolog', 'vivaist'],
    'RESEARCHER': ['ricercator', 'sperimentazion', 'dottorand', 'docent',
                   'professor', 'ricerca scientific'],
    'EDUCATION_INSTITUTION': ['universit', 'facolt', 'dipartiment', 'scuola',
                              'istituto tecnic', 'ateneo'],
    'PUBLIC_RESEARCH_INSTITUTION': ['crea', 'cnr ', 'consiglio nazionale delle ricerche'],
    'PUBLIC_AUTHORITY': ['servizio fitosanitar', 'regione ', 'assessorat',
                         'ente nazionale'],
    'COOPERATIVE': ['cooperativ', 'consorzi'],
    'PRODUCER_ORGANISATION': ['coldiretti', 'confagricoltura', 'condifesa',
                              'organizzazione dei produttori'],
    'INDUSTRY_ASSOCIATION': ['associazion', 'federazion'],
    'TECHNICAL_MEDIA': ['rivista', 'redazion', 'testata', 'editorial',
                        'divulgaz', 'notizie per'],
    'COMPANY': ['azienda agricol', 's.r.l', 'srl', 's.p.a', 'spa ', 'societ'],
}

# ── AUTODECLARAÇÃO EM PRIMEIRA PESSOA ────────────────────────────────────────
# ⚠️ MEDIDO EM 2026-09-03, E É O CAMPO MAIS IMPORTANTE DESTE ARQUIVO.
# Dos 8 primeiros TECHNICAL_ADVISER, só 4 eram uma PESSOA declarando o próprio
# papel. Os outros 4 eram organização citando a palavra:
#
#   sumitomo chemical Italy   "i risultati degli studi dei nostri tecnici agronomi"
#   Consorzi Agrari d'Italia  "troverai consigli agronomici"
#   Confraternita Valdobb.    "quattro lungimiranti enologi (umberto bortolotti...)"
#   Agronotizie               lista de seções do site: "agronomia, economia..."
#
# E no balde RESEARCHER o erro fica ainda mais nu:
#
#   axsm31    "la scoperta del RICERCATORE alessandro mendini"   ← terceiro citado
#   Mr Green  "ho la curiosità del RICERCATORE"                  ← metáfora
#
# São exatamente os dois erros que a `ROLE_RULE` desta casa previu — "terceiros
# citados" e "palavras de notícia" — acontecendo na primeira passada.
#
#     A PALAVRA "AGRÔNOMO" NA PÁGINA NÃO FAZ DE NINGUÉM UM AGRÔNOMO.
#     QUEM DIZ "SOU" É OUTRA COISA DE QUEM DIZ "NOSSOS".
#
# Isto não vira desempate: vira CAMPO. Quem procura PESSOA filtra por ele; quem
# procura organização técnica ignora. As duas perguntas são legítimas e diferentes.
PRIMEIRA_PESSOA = ['sono un', 'sono una', 'mi chiamo', 'sono il', 'sono la',
                   'il mio nome', 'mi occupo', 'lavoro come', 'aiuto ', 'vi aiuto',
                   'condivido', 'la mia esperienza', 'nel mio', 'nella mia']
TERCEIRO_CITADO = ['nostri ', 'nostro ', 'nostra ', 'i nostri', 'del nostro',
                   'troverai', 'troverete', 'grazie ai', 'con i nostri']


# Marcadores de PLATEIA que contradizem papel técnico. Não desempatam sozinhos:
# eles publicam um CONFLITO, porque desempate silencioso é o que esconde o erro.
HOBBY = ['orto', 'giardin', 'balcon', 'in vaso', 'hobbist', 'appassionat',
         'fai da te', 'casa e giardino']


def normaliza(t):
    t = unicodedata.normalize('NFD', str(t or '').lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', t)


def acha(raiz, texto):
    """→ lista de (trecho_literal, posicao). Fronteira de palavra SEMPRE.

    O guarda de fronteira nao consertou nada neste corpus — medido, zero falsos.
    Ele fica porque `zootecnico` contem `tecnic`, e basta um canal de zootecnia
    entrar para ele passar a valer. Guarda que so' se instala depois do acidente
    e' guarda que chega tarde.
    """
    achados = []
    for m in re.finditer(r'(?<![a-z0-9])%s[a-z]*' % re.escape(raiz), texto):
        ini = max(0, m.start() - 60)
        fim = min(len(texto), m.end() + 60)
        achados.append((texto[ini:fim].strip(), m.start()))
    return achados


def classificar(descricao, nome_da_conta='', plateia=NAO_SEI):
    """→ dict. A regra, sozinha numa funcao, para a prova chamar ELA e nao uma copia."""
    d = normaliza(descricao)
    nome = normaliza(nome_da_conta)
    if not d:
        return {'ROLE_CANDIDATE_FROM_PROSE': 'NOT_DECLARED',
                'POR_QUE': 'o canal nao publica descricao — isto NAO e evidencia de '
                           'que ele nao tem papel, e a falta dela',
                'ROLE_EVIDENCE': [], 'PAPEIS_ACHADOS': [], 'CONFLITO_COM_PLATEIA': False}

    achados, evid = {}, []
    for papel, raizes in RAIZES.items():
        for r in raizes:
            for trecho, pos in acha(r, d):
                achados.setdefault(papel, []).append(r)
                evid.append({'PAPEL': papel, 'RAIZ': r, 'TRECHO_LITERAL': trecho,
                             'RAIZ_ESTA_NO_NOME_DA_CONTA': bool(r in nome)})

    if not achados:
        return {'ROLE_CANDIDATE_FROM_PROSE': 'NOT_DECLARED',
                'POR_QUE': 'nenhuma raiz de cargo aparece na descricao',
                'ROLE_EVIDENCE': [], 'PAPEIS_ACHADOS': [], 'CONFLITO_COM_PLATEIA': False}

    hob = [h for h in HOBBY if acha(h, d)]
    conflito = bool(hob) and 'TECHNICAL_ADVISER' in achados
    eu = [t for t in PRIMEIRA_PESSOA if t in d]
    eles = [t for t in TERCEIRO_CITADO if t in d]
    voz = ('PRIMEIRA_PESSOA' if eu and not eles else
           'TERCEIRO_CITADO' if eles and not eu else
           'AMBAS' if eu and eles else 'NAO_DECLARADA')
    extra = {'VOZ_DA_DESCRICAO': voz, 'MARCAS_DE_PRIMEIRA_PESSOA': eu,
             'MARCAS_DE_TERCEIRO': eles,
             'VOZ_POR_QUE': ('quem diz "sou" declara o proprio papel; quem diz "nossos" '
                             'fala de terceiros. A palavra agronomo na pagina nao faz de '
                             'ninguem um agronomo.')}

    # ⚠️ AMBIGUOUS E' ESTADO, NAO EMPATE A RESOLVER. A casa escreveu: "quando dois
    # papeis distintos sao declarados, nao se desempata por ordem de regex".
    if len(achados) > 1:
        return {'ROLE_CANDIDATE_FROM_PROSE': 'AMBIGUOUS',
                'POR_QUE': 'a descricao declara %d papeis distintos (%s), e nao se '
                           'desempata por ordem de regex'
                           % (len(achados), ', '.join(sorted(achados))),
                'ROLE_EVIDENCE': evid, 'PAPEIS_ACHADOS': sorted(achados),
                'CONFLITO_COM_PLATEIA': conflito,
                'MARCADORES_DE_HOBBY': hob, **extra}

    papel = next(iter(achados))
    return {'ROLE_CANDIDATE_FROM_PROSE': papel,
            'POR_QUE': 'unica familia de papel declarada na prosa: %s'
                       % ', '.join(sorted(set(achados[papel]))),
            'ROLE_EVIDENCE': evid, 'PAPEIS_ACHADOS': [papel],
            'CONFLITO_COM_PLATEIA': conflito,
            'MARCADORES_DE_HOBBY': hob, **extra}


def _ler(pasta, nome):
    p = os.path.join(pasta, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def fase_medir():
    canais = _ler(JANELA, 'CANAIS.json')
    idioma = _ler(RELEV, 'CANAIS-IDIOMA.json')
    if not canais:
        print('sem CANAIS.json — rode `youtube_janela.py canais` antes')
        return 1
    idi = ({i['ACCOUNT_HANDLE']: i['TITLE_LANGUAGE_DOMINANT'] for i in idioma['ITEMS']}
           if idioma else {})

    itens, por_estado, com_desc, conflitos = [], {}, 0, 0
    for c in canais['CANAIS']:
        h = c.get('ACCOUNT_HANDLE')
        if idi and idi.get(h) != 'IT':
            continue
        desc = c.get('DESCRIPTION')
        desc = '' if desc in (None, NAO_SEI) else desc
        if desc:
            com_desc += 1
        r = classificar(desc, h, c.get('CHANNEL_AUDIENCE_KIND', NAO_SEI))
        e = r['ROLE_CANDIDATE_FROM_PROSE']
        por_estado[e] = por_estado.get(e, 0) + 1
        if r.get('CONFLITO_COM_PLATEIA'):
            conflitos += 1
        itens.append(dict(r, **{
            'ACCOUNT_HANDLE': h,
            'CHANNEL_TITLE': c.get('CHANNEL_TITLE', NAO_SEI),
            'ACCOUNT_URL': c.get('ACCOUNT_URL', NAO_SEI),
            'SUBSCRIBERS': c.get('SUBSCRIBERS', NAO_SEI),
            'TITLE_LANGUAGE_DOMINANT': idi.get(h, NAO_SEI),
            'DECLARED_ROLE': 'NOT_TESTED',
            'DECLARED_ROLE_POR_QUE': ('prosa nao promove a DECLARED_ROLE. A promocao '
                                      'exige fonte estruturada — LinkedIn Full, ou o '
                                      'registro profissional italiano.'),
        }))

    os.makedirs(SAIDA, exist_ok=True)
    import datetime
    corpo = {
        'SOURCE_ID': 'YOUTUBE-PAPEL/PAPEL-CANDIDATO-IT',
        'source': 'derivado das descricoes ja coletadas — nenhuma coleta nova, custo zero',
        'SOURCE_LOCATION': 'derivado — interno',
        'FACT_LOCATION': 'IT', 'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.datetime.now(
            datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'APIFY_RUNS': 0, 'COST_USD': 0, 'MISSION': MISSION,
        'O_QUE_ISTO_E': ('o papel que o canal DECLARA de si na propria descricao, com o '
                         'trecho literal que decidiu. E candidato, nao papel.'),
        'POR_QUE_NAO_E_DECLARED_ROLE': (
            'a ROLE_RULE desta casa proibe prosa livre para decidir papel, por tres '
            'erros ja medidos: terceiros citados, palavras de noticia, e token dentro '
            'de palavra (ftalimida contem imida). No YouTube SO existe prosa livre. '
            'PROSA NAO DECIDE PAPEL — ELA INDICA ONDE PERGUNTAR.'),
        'COMO_PROMOVER': ('fonte estruturada: LinkedIn em modo Full (cargo declarado), '
                          'ou o registro profissional italiano (CONAF / Ordine dei '
                          'Dottori Agronomi e Forestali, Collegio dei Periti Agrari, '
                          'Agrotecnici), que e o unico lugar onde "dottore agronomo" e '
                          'campo declarado por lei e nao headline.'),
        'O_LEXICO_E_UMA_APOSTA': ('nenhum arquivo desta casa tinha vocabulario de cargo '
                                  'italiano. Este e o primeiro. Cada raiz e lista '
                                  'escrita a mao, conferivel contra o corpus.'),
        'FRONTEIRA_DE_PALAVRA': ('ligada e MEDIDA: zero falsos neste corpus (agronom 16 '
                                 'com e sem fronteira; tecnic 23 com e sem). Ela fica '
                                 'porque `zootecnico` contem `tecnic`.'),
        'O_ERRO_QUE_A_FRONTEIRA_NAO_PEGA': (
            '`Orto Da Coltivare` declara agronom, tecnic e divulgaz, e e canal de horta '
            'domestica. O CANAL QUE CITA UM AGRONOMO NAO E UM AGRONOMO. Por isso o '
            'conflito com a plateia e publicado, nunca desempatado em silencio.'),
        'CANAIS_MEDIDOS': len(itens),
        'CANAIS_COM_DESCRICAO': com_desc,
        'BY_ROLE_CANDIDATE': por_estado,
        'CONFLITOS_COM_PLATEIA': conflitos,
        'ITEMS': itens,
    }
    with open(os.path.join(SAIDA, 'PAPEL-CANDIDATO-IT.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('canais italianos medidos: %d (com descricao: %d)' % (len(itens), com_desc))
    for k, n in sorted(por_estado.items(), key=lambda x: -x[1]):
        print('   %-32s %s' % (k, n))
    print('conflitos papel-tecnico x plateia-hobby: %d' % conflitos)
    print('gravado: data/samples/YOUTUBE-PAPEL/PAPEL-CANDIDATO-IT.json')
    return 0


def _testes():
    falhas = []

    def diz(cond, oq, det=''):
        print(('  OK   ' if cond else '  FALHA ') + oq + (' · ' + det if det else ''))
        if not cond:
            falhas.append(oq)

    # 1 · O ACERTO QUE JUSTIFICA A ROTA — texto real do corpus.
    r = classificar('Il canale ufficiale di Agralia, studio di agronomia di Brescia. '
                    'Agralia è un team di Dottori Agronomi che offrono servizi alle '
                    'aziende agricole.', 'Agralia studio di agronomia')
    diz(r['ROLE_CANDIDATE_FROM_PROSE'] == 'TECHNICAL_ADVISER',
        'estudio de agronomia vira TECHNICAL_ADVISER', r['ROLE_CANDIDATE_FROM_PROSE'])
    diz(any('agronomi' in e['TRECHO_LITERAL'] for e in r['ROLE_EVIDENCE']),
        'o trecho literal que decidiu viaja junto')

    # 2 · O ERRO QUE A FRONTEIRA NAO PEGA — texto real do corpus.
    r = classificar('Qui trovi consigli su come coltivare orto e frutteto con metodo '
                    'biologico, con un agronomo. Video di potatura e innesti.',
                    'Orto Da Coltivare')
    diz(r['CONFLITO_COM_PLATEIA'] is True,
        'canal de horta com "agronomo" publica CONFLITO, nao papel limpo',
        'hobby=%s' % r.get('MARCADORES_DE_HOBBY'))

    # 3 · `zootecnico` NAO pode virar `tecnic`. E o ftalimida/imida desta rodada.
    r = classificar('Tecnozoo opera nel panorama zootecnico nazionale da 40 anni.',
                    'Tecnozoo')
    diz('TECHNICAL_ADVISER' not in r['PAPEIS_ACHADOS'],
        'zootecnico NAO vira assistencia tecnica', str(r['PAPEIS_ACHADOS']))

    # 4 · AMBIGUOUS e' ESTADO. A casa escreveu: nao se desempata por ordem de regex.
    r = classificar('Societa cooperativa che promuove ricerca e sperimentazione, '
                    'con il nostro team di agronomi.', 'RiNova')
    diz(r['ROLE_CANDIDATE_FROM_PROSE'] == 'AMBIGUOUS',
        'dois papeis declarados viram AMBIGUOUS, nao o primeiro da lista',
        str(r['PAPEIS_ACHADOS']))

    # 5 · Sem descricao NAO e' "nao tem papel". Geladeira vazia != luz cortada.
    r = classificar('', 'Canal Qualquer')
    diz(r['ROLE_CANDIDATE_FROM_PROSE'] == 'NOT_DECLARED' and 'falta dela' in r['POR_QUE'],
        'sem descricao e falta de evidencia, nao evidencia de ausencia')

    # 6 · A VOZ SEPARA QUEM DIZ "SOU" DE QUEM DIZ "NOSSOS" — os dois erros medidos.
    r = classificar('sono un enologo - agronomo con un solo scopo', 'Matteo Pala')
    diz(r['VOZ_DA_DESCRICAO'] == 'PRIMEIRA_PESSOA',
        'quem diz "sono un agronomo" sai PRIMEIRA_PESSOA')
    r = classificar('i risultati degli studi dei nostri tecnici agronomi in campo', 'x')
    diz(r['VOZ_DA_DESCRICAO'] == 'TERCEIRO_CITADO',
        'empresa que diz "nossos tecnicos" sai TERCEIRO_CITADO')
    r = classificar('la scoperta del ricercatore alessandro mendini', 'axsm31')
    diz(r['VOZ_DA_DESCRICAO'] == 'NAO_DECLARADA',
        'terceiro citado por nome nao vira autodeclaracao')

    # 7 · Nunca produzir DECLARED_ROLE a partir de prosa.
    r = classificar('Sono un dottore agronomo libero professionista.', 'Mario Rossi')
    diz('DECLARED_ROLE' not in r,
        'a funcao nunca devolve DECLARED_ROLE — so candidato')

    print()
    print('FALHAS: %d' % len(falhas))
    return 1 if falhas else 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'medir'
    if cmd == 'medir':
        raise SystemExit(fase_medir())
    if cmd == 'teste':
        raise SystemExit(_testes())
    print('uso: youtube_papel.py {medir|teste}')
    raise SystemExit(2)
