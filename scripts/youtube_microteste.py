#!/usr/bin/env python3
"""
O TESTE PEQUENO — dez objetos, para decidir se vale gastar as horas dos cento e cinquenta.

    py scripts/youtube_microteste.py escolher      # GRÁTIS: quais dez, e por quê
    py scripts/youtube_microteste.py rodar         # legenda → escada → medição
    py scripts/youtube_microteste.py medir         # só a medição, sobre o que já existe
    py scripts/youtube_microteste.py tudo

POR QUE DEZ, E NÃO CENTO E CINQUENTA
======================================
Porque a pergunta ainda não é "quanto texto o acervo ganha". A pergunta é "a escada
funciona, e o texto a mais muda alguma classificação". Rodar os 150 antes de responder
isso é comprar a resposta pelo preço mais caro que ela tem.

    MEDIR PRIMEIRO É MAIS BARATO QUE DESFAZER DEPOIS.

Este arquivo não escala nada, não muda régua nenhuma e não decide sozinho. Ele monta
a prova e mostra o número — quem decide é quem manda.

A ESCOLHA DOS DEZ É DECLARADA, E NÃO É SORTEIO
================================================
A missão pede quatro grupos: alguns com legenda funcionando, alguns sem legenda
utilizável, alguns que hoje estão NÃO SEI, e pelo menos um vídeo agrícola conhecido.

Só que os três primeiros grupos **não se pode escolher antes de perguntar**: saber se
um vídeo tem legenda é o resultado do teste, não a entrada dele. Prometer o contrário
seria escolher a resposta.

    QUEM ESCOLHE PELO RESULTADO NÃO TESTA NADA: ELE CONFIRMA.

Então a escolha é feita pelo que se sabe de graça ANTES — canal, país, duração e
termos técnicos no título — e a distribuição pelos quatro grupos é RELATADA depois,
com o nome de cada vídeo. O único grupo escolhível de véspera é o agrícola: ele sai do
léxico do `sensor_medir.py`, lido pelo `youtube_relevancia.py`, sem cópia e sem
alteração.

E dois filtros duros, os dois por economia de hora de máquina:

  * **Só contas DENTRO do lote congelado.** `youtube_janela.contas()` colhe também a
    `CortevaBiologicals`, que o lote registrou em `EXCLUDED_ACCOUNTS` — 30 dos 240
    vídeos. Transcrever conta excluída é gastar hora de máquina fora do recorte.
  * **Duração mediana ou menor.** Ao preço medido, cada minuto de áudio custa segundos
    de máquina; o teste não precisa dos vídeos mais longos para provar a escada.

AS RÉGUAS SÃO AS QUE JÁ EXISTEM, E ELAS NÃO FORAM TOCADAS
===========================================================
A medição do antes e do depois chama `sensor_medir.classificar_conteudo()` e
`youtube_relevancia.veredito()` — as funções de verdade, não uma cópia dos `if` delas.
A lição é do `diario.py` do Brasil: prova que copia a regra para dentro de si confere
uma cópia da regra e continua verde depois que a regra muda.

    É CONFERIR A CHAVE CONTRA UMA FOTO DA CHAVE.

O QUE "NÃO SEI" QUER DIZER AQUI, COM O NOME QUE A CASA JÁ USA
===============================================================
`classificar_conteudo` devolve `NOT_ENOUGH_TEXT` quando descrição e transcrição somam
menos de 200 caracteres. Esse é o NÃO SEI desta medição, e ele não é um defeito da
régua: é a régua se recusando a promover um título a observação técnica. A lição do
Xylella está escrita na própria função.

    TÍTULO NÃO VIRA OBSERVAÇÃO TÉCNICA SOZINHO — E É POR ISSO QUE O TEXTO IMPORTA.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sensor_medir as sm             # noqa: E402  — dono do léxico e do classificador
import youtube_janela as yj           # noqa: E402  — dono canônico da coleta do YouTube
import youtube_relevancia as yr       # noqa: E402  — dono das réguas, NÃO alterado
import youtube_transcrever as yt      # noqa: E402  — a escada

SAMPLES = os.path.join(ROOT, 'data', 'samples')
JANELA = os.path.join(SAMPLES, 'YOUTUBE-JANELA')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-TRANSCRICOES')

NAO_SEI = 'NOT_KNOWN'
MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
QUANTOS = int(os.environ.get('YT_MICROTESTE_N') or 10)

# ── COMO A CLASSIFICAÇÃO DE `sensor_medir` VIRA AS QUATRO CONTAS DA MISSÃO ──────────
# Isto é um AGRUPAMENTO da saída da régua, não uma régua nova: nenhum vídeo é
# classificado aqui. Os nomes da esquerda são os que a missão pediu; os da direita são
# os que `classificar_conteudo` realmente devolve.
NAO_SEI_TIPOS = {'NOT_ENOUGH_TEXT'}
FIELD_SIGNAL_TIPOS = {'FIELD_OBSERVATION'}
AG_RELEVANT_TIPOS = {'FIELD_OBSERVATION', 'RESEARCH_COMMUNICATION',
                     'TECHNICAL_INTERPRETATION'}
OFF_TOPIC_TIPOS = {'MARKETING', 'NEWS_REPOST', 'EVENT_PROMOTION', 'NOISE'}


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/YOUTUBE-TRANSCRICOES/' + nome


# ═══════════════════════════════════════════════════════════════════ A ESCOLHA

def escolher(quantos=QUANTOS):
    """→ (escolhidos, diario_da_escolha). Determinística: nada de sorteio.

    Sorteio num teste de dez faz duas execuções discordarem sem que ninguém tenha
    mudado nada — e aí a medição não pode ser conferida por outra pessoa.
    """
    objetos = yt._ler_json(os.path.join(JANELA, 'OBJETOS.json'))
    if not objetos:
        return None, ['sem OBJETOS.json — rode `py scripts/youtube_janela.py objetos`']
    itens = objetos['ITEMS']
    lote = yt.paises_do_lote()
    dic = yr.dicionario()

    diario = ['universo lido: %d objetos' % len(itens)]

    dentro = [i for i in itens if (lote.get(i.get('ACCOUNT_HANDLE')) or {}).get('NO_LOTE')]
    fora = len(itens) - len(dentro)
    diario.append('fora do lote congelado, descartados: %d (conta em EXCLUDED_ACCOUNTS)'
                  % fora)

    duracoes = sorted(i['DURATION_S'] for i in dentro
                      if isinstance(i.get('DURATION_S'), (int, float)))
    mediana = duracoes[len(duracoes) // 2] if duracoes else 0
    curtos = [i for i in dentro
              if isinstance(i.get('DURATION_S'), (int, float))
              and 0 < i['DURATION_S'] <= mediana]
    diario.append('mediana de duração do lote: %d s — ficam os %d objetos até a mediana'
                  % (mediana, len(curtos)))

    # Termos técnicos no TÍTULO, pelo léxico do dono dele. Isto ORDENA; não promove.
    for i in curtos:
        achados, _n = yr.varre(i.get('TITLE') or '', dic)
        i['_TERMOS'] = sorted(achados)

    agricolas = [i for i in curtos if i['_TERMOS']]
    diario.append('com termo técnico no título (candidatos ao grupo D): %d' % len(agricolas))

    # Um por canal, primeiro os agrícolas, para que os dez não saiam todos do mesmo
    # canal — um teste de dez vídeos de UM canal mede aquele canal, não a escada.
    escolhidos, por_canal = [], {}
    for pool in (sorted(agricolas, key=lambda i: (-len(i['_TERMOS']), i['DURATION_S'])),
                 sorted(curtos, key=lambda i: i['DURATION_S'])):
        for i in pool:
            if len(escolhidos) >= quantos:
                break
            h = i.get('ACCOUNT_HANDLE')
            if any(e['VIDEO_ID'] == i['VIDEO_ID'] for e in escolhidos):
                continue
            if por_canal.get(h, 0) >= 2:
                continue
            por_canal[h] = por_canal.get(h, 0) + 1
            escolhidos.append(i)
    diario.append('escolhidos: %d, de %d canais, no máximo 2 por canal'
                  % (len(escolhidos), len(por_canal)))
    diario.append('critério declarado: dentro do lote → até a mediana de duração → mais '
                  'termos técnicos no título → mais curto primeiro → no máximo 2 por canal')
    diario.append('o que NÃO foi usado para escolher: se o vídeo tem legenda. Isso é o '
                  'RESULTADO do teste, e escolher por ele seria escolher a resposta.')
    return escolhidos, diario


def fase_escolher():
    escolhidos, diario = escolher()
    for d in diario:
        print('  %s' % d)
    if not escolhidos:
        return 1
    print()
    seg = sum(i.get('DURATION_S') or 0 for i in escolhidos)
    for i in escolhidos:
        print('  %-13s %4ss %-24s %-18s %s'
              % (i['VIDEO_ID'], i.get('DURATION_S'), str(i.get('ACCOUNT_HANDLE'))[:24],
                 ','.join(i['_TERMOS'])[:18] or '—', str(i.get('TITLE'))[:38]))
    print()
    print('áudio total se TODOS forem ao whisper: %.1f min' % (seg / 60.0))
    print('a 5,5x medido neste contêiner: ~%.1f min de máquina · 0,00 USD' % (seg / 5.5 / 60))
    return 0


# ═══════════════════════════════════════════════════════════════════ A MEDIÇÃO

def _classificar(titulo, texto):
    """As réguas de verdade, chamadas como elas são. → dict com os dois vereditos."""
    tipo, evidencia = sm.classificar_conteudo(titulo, '', texto or '')
    achados, n_palavras = yr.varre('%s %s' % (titulo or '', texto or ''), yr.dicionario())
    v, por_que = yr.veredito(achados, n_palavras, yr.dicionario())
    return {
        'CONTENT_TYPE': tipo,
        'CONTENT_EVIDENCE': evidencia,
        'VOCAB_VEREDITO': v,
        'VOCAB_POR_QUE': por_que,
        'N_PALAVRAS': n_palavras,
        'TERMOS': sorted(achados),
        'NAO_SEI': tipo in NAO_SEI_TIPOS,
        'FIELD_SIGNAL': tipo in FIELD_SIGNAL_TIPOS,
        'AG_RELEVANT': tipo in AG_RELEVANT_TIPOS,
        'OFF_TOPIC': tipo in OFF_TOPIC_TIPOS,
    }


def _contas(linhas, chave):
    return {
        'NAO_SEI': sum(1 for l in linhas if l[chave]['NAO_SEI']),
        'FIELD_SIGNAL': sum(1 for l in linhas if l[chave]['FIELD_SIGNAL']),
        'AG_RELEVANT': sum(1 for l in linhas if l[chave]['AG_RELEVANT']),
        'OFF_TOPIC': sum(1 for l in linhas if l[chave]['OFF_TOPIC']),
    }


def medir():
    """Compara TITLE_ONLY com CAPTION_OR_WHISPER sobre o que a escada gravou. → 0/1."""
    texto = yt._ler_json(os.path.join(SAIDA, 'TEXTO.json'))
    if not texto:
        print('sem TEXTO.json — rode `py scripts/youtube_microteste.py rodar` antes')
        return 1
    itens = texto['ITEMS']

    linhas = []
    for i in itens:
        titulo = i.get('TITLE') or ''
        ganho = i.get('TRANSCRIPT') or ''
        antes = _classificar(titulo, '')
        depois = _classificar(titulo, ganho)
        linhas.append({
            'VIDEO_ID': i['VIDEO_ID'],
            'SOURCE_ID': i.get('SOURCE_ID'),
            'SOURCE_URL': i.get('SOURCE_URL'),
            'ACCOUNT_HANDLE': i.get('ACCOUNT_HANDLE'),
            'COUNTRY': i.get('COUNTRY'),
            'LANGUAGE': i.get('LANGUAGE'),
            'TITLE': titulo,
            'CAPTION_STATE': i.get('CAPTION_STATE'),
            'WHISPER_STATE': i.get('WHISPER_STATE'),
            'TEXT_SOURCE': i.get('TEXT_SOURCE'),
            'TEXT_CHARS_GANHOS': len(ganho),
            'TITLE_ONLY': antes,
            'CAPTION_OR_WHISPER': depois,
            'MUDOU': antes['CONTENT_TYPE'] != depois['CONTENT_TYPE'],
        })

    antes_c = _contas(linhas, 'TITLE_ONLY')
    depois_c = _contas(linhas, 'CAPTION_OR_WHISPER')

    exemplos = _cinco_exemplos(linhas)

    corpo = {
        'SOURCE_ID': 'YOUTUBE-TRANSCRICOES/MICROTESTE',
        'source': ('medição do que o texto a mais muda na classificação, sobre as réguas '
                   'que já existem — nenhuma régua foi alterada'),
        'SOURCE_LOCATION': 'derivado — YOUTUBE-TRANSCRICOES/TEXTO e as réguas desta casa',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da conta',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'captured_at': yt.hoje(), 'CAPTURED_AT': yt.agora(),
        'MISSION': MISSION, 'APIFY_RUNS': 0, 'COST_USD': 0, 'PAID_API_COST_USD': 0,
        'AS_REGUAS_NAO_FORAM_TOCADAS': (
            'a classificação chama sensor_medir.classificar_conteudo() e '
            'youtube_relevancia.veredito() — as funções de verdade, não uma cópia dos '
            'ifs delas. Prova que copia a regra confere uma foto da chave.'),
        'O_QUE_NAO_SEI_QUER_DIZER': (
            'NOT_ENOUGH_TEXT: descrição e transcrição somam menos de 200 caracteres, e a '
            'régua se recusa a promover um título a observação técnica. Não é defeito da '
            'régua — é a lição do Xylella escrita dentro dela.'),
        'TEST_OBJECTS': len(linhas),
        **_veredito_da_missao(linhas, texto),
        'NAO_SEI_BEFORE': antes_c['NAO_SEI'], 'NAO_SEI_AFTER': depois_c['NAO_SEI'],
        'AG_RELEVANT_BEFORE': antes_c['AG_RELEVANT'], 'AG_RELEVANT_AFTER': depois_c['AG_RELEVANT'],
        'FIELD_SIGNAL_BEFORE': antes_c['FIELD_SIGNAL'], 'FIELD_SIGNAL_AFTER': depois_c['FIELD_SIGNAL'],
        'OFF_TOPIC_BEFORE': antes_c['OFF_TOPIC'], 'OFF_TOPIC_AFTER': depois_c['OFF_TOPIC'],
        # ── DE QUAL EXECUÇÃO É ESTE CUSTO ─────────────────────────────────────
        # `rodar` executa a escada DUAS vezes de propósito, para provar o cache. A
        # segunda é toda em cache e gasta zero. Publicar só o número dela diria
        # "custo zero" sobre um lote que já foi pago — e essa seria a mentira mais
        # confortável deste arquivo inteiro.
        #
        #     O CUSTO NÃO SOME PORQUE A SEGUNDA LEITURA FOI DE GRAÇA.
        'TOTAL_AUDIO_MINUTES_ULTIMA_EXECUCAO': texto.get('TOTAL_AUDIO_MINUTES'),
        'TOTAL_MACHINE_SECONDS_ULTIMA_EXECUCAO': texto.get('TOTAL_MACHINE_SECONDS'),
        'TOTAL_AUDIO_MINUTES': texto.get('TOTAL_AUDIO_MINUTES_ACUMULADO',
                                         texto.get('TOTAL_AUDIO_MINUTES')),
        'TOTAL_MACHINE_SECONDS': texto.get('TOTAL_MACHINE_SECONDS_ACUMULADO',
                                           texto.get('TOTAL_MACHINE_SECONDS')),
        'DE_QUAL_EXECUCAO_VEM_O_CUSTO': (
            'TOTAL_* é o ACUMULADO do acervo — tudo o que já foi pago em hora de '
            'máquina por estes vídeos. TOTAL_*_ULTIMA_EXECUCAO é o que a última '
            'passada gastou, e numa passada toda em cache ele é zero de verdade.'),
        'CUSTO_NAO_E_ZERO_ABSOLUTO': (
            'PAID_API_COST_USD = 0 porque o reconhecimento roda nesta máquina. O custo '
            'real é TOTAL_MACHINE_SECONDS, e ele não é zero.'),
        'REALTIME_FACTOR': texto.get('REALTIME_FACTOR'),
        'CAPTION_HITS': texto.get('CAPTION_HITS'),
        'WHISPER_FALLBACKS': texto.get('WHISPER_FALLBACKS'),
        'WHISPER_SUCCESS': texto.get('WHISPER_SUCCESS'),
        'WHISPER_FAILURES': texto.get('WHISPER_FAILURES'),
        'CACHE_HITS': texto.get('CACHE_HITS'),
        'IDENTITY_ERRORS': texto.get('IDENTITY_ERRORS'),
        'NEW_ENTITIES_FROM_CONTENT': texto.get('NEW_ENTITIES_FROM_CONTENT'),
        'ROLE_FROM_CONTENT': texto.get('ROLE_FROM_CONTENT'),
        'DOCUMENT_WITHOUT_SOURCE_ID': texto.get('DOCUMENT_WITHOUT_SOURCE_ID'),
        'SCALE_TO_150': 'NAO — esta medição existe para que alguém decida, não para decidir',
        'SCALE_TO_89_CHANNELS': 'NAO',
        'CINCO_EXEMPLOS': exemplos,
        'ITEMS': linhas,
    }
    caminho = _gravar('MICROTESTE.json', corpo)

    print('gravado: %s' % caminho)
    print()
    print('  %-22s %8s %8s' % ('', 'ANTES', 'DEPOIS'))
    for k in ('NAO_SEI', 'AG_RELEVANT', 'FIELD_SIGNAL', 'OFF_TOPIC'):
        print('  %-22s %8d %8d' % (k, antes_c[k], depois_c[k]))
    print()
    for nome, e in exemplos.items():
        if e:
            print('  %-28s %-13s %s' % (nome, e['VIDEO_ID'], e['POR_QUE'][:70]))
        else:
            print('  %-28s (nenhum caso deste tipo neste microteste)' % nome)
    return 0


def _veredito_da_missao(linhas, texto):
    """Os campos que a pergunta "vale a pena o whisper?" exige — com o denominador à vista.

    RECOVERY_RATE é a razão mais fácil de mentir deste arquivo inteiro. O numerador é
    honesto sozinho: WHISPER_SUCCESS é um texto que existe. O denominador não é.
    Quantos vídeos PRECISARAM do whisper só é uma pergunta sobre a LEGENDA quando o
    denominador é feito de vídeos que de fato não têm legenda. Um 429 na porta da
    legenda também empurra o vídeo para o whisper — e uma taxa calculada sobre esse
    denominador mede a MINHA REDE, com o nome da legenda do concorrente.

        UMA TAXA SEM O DENOMINADOR À VISTA É UMA OPINIÃO COM CASAS DECIMAIS.

    Por isso o denominador é publicado quebrado em duas partes, e a própria taxa
    carrega um campo dizendo se ela pode ser lida como cobertura de legenda ou se ela
    é, naquela rodada, um retrato do ambiente.
    """
    por_leg = texto.get('POR_ESTADO_DE_LEGENDA') or {}
    ausente = int(por_leg.get(yt.NO_CAPTION_CONFIRMED, 0))
    inconclusivo = sum(int(por_leg.get(e, 0)) for e in (
        yt.CAPTION_ENVIRONMENT_FAILURE, yt.CAPTION_FETCH_FAILURE,
        yt.CAPTION_PARSE_FAILURE, yt.CAPTION_DELIVERED_EMPTY, yt.CAPTION_NOT_TESTED))

    precisou = int(texto.get('WHISPER_FALLBACKS') or 0)
    recuperou = int(texto.get('WHISPER_SUCCESS') or 0)
    taxa = round(recuperou / precisou, 3) if precisou else yt.NAO_SEI

    # Cobertura é uma contagem de vídeos com texto ALÉM do título — não de caracteres.
    # Um vídeo com 40 mil caracteres e um com 400 contam UM cada: a régua desta casa
    # decide por conteúdo, e dobrar o texto de quem já falava não cobre quem calava.
    com_texto = sum(1 for l in linhas if l.get('TEXT_SOURCE') != 'TITLE_ONLY')
    n = len(linhas)

    maq = texto.get('TOTAL_MACHINE_SECONDS_ACUMULADO', texto.get('TOTAL_MACHINE_SECONDS'))
    transcritos = sum(1 for l in linhas if l.get('TEXT_SOURCE') == 'WHISPER_LOCAL')
    media = (round(float(maq) / transcritos, 1)
             if transcritos and isinstance(maq, (int, float)) else yt.NAO_SEI)

    return {
        'VIDEOS_TESTADOS': n,
        'NATIVE_CAPTION_OK': texto.get('CAPTION_HITS'),
        'CAPTION_ABSENT_CONFIRMED': ausente,
        'CAPTION_INCONCLUSIVE': inconclusivo,
        'O_QUE_O_DENOMINADOR_TEM_DENTRO': (
            'WHISPER_NEEDED = %d. Destes, %d são vídeos que o player declarou SEM faixa '
            '(NO_CAPTION_CONFIRMED) e %d são confissões sobre a minha rede ou o meu '
            'leitor. Só a primeira parte é uma pergunta sobre a legenda.'
            % (precisou, ausente, inconclusivo)),
        'WHISPER_NEEDED': precisou,
        'RECOVERY_RATE': taxa,
        'RECOVERY_RATE_MEDE_A_LEGENDA': (
            'SIM' if precisou and inconclusivo == 0 else
            'NAO — %d dos %d vídeos do denominador chegaram ao whisper por falha de '
            'ambiente, não por ausência de legenda. Nesta rodada a taxa retrata o '
            'ambiente.' % (inconclusivo, precisou) if precisou else
            'NAO_SE_APLICA — nenhum vídeo precisou do whisper nesta rodada'),
        'COVERAGE_BEFORE': 0,
        'COVERAGE_AFTER': com_texto,
        'COVERAGE_GAIN': ('%d/%d vídeos passaram a ter texto além do título' % (com_texto, n)),
        'O_QUE_COVERAGE_NAO_DIZ': (
            'que a classificação mudou. Texto a mais é matéria-prima; o que a régua faz '
            'com ele está em NAO_SEI_BEFORE/AFTER, e as duas medidas podem discordar.'),
        'AVG_MACHINE_SECONDS_PER_TRANSCRIPTION': media,
        'ESTIMATED_COST_USD': 0,
        'O_QUE_ESTIMATED_COST_ESCONDERIA': (
            'nada é faturado porque o reconhecimento roda nesta máquina. A conta que '
            'existe é AVG_MACHINE_SECONDS_PER_TRANSCRIPTION × número de vídeos, e ela '
            'é paga em tempo do runner.'),
    }


def _cinco_exemplos(linhas):
    """Os cinco casos concretos que a missão pede. Ausência é declarada, não escondida."""
    def achar(cond):
        for l in linhas:
            if cond(l):
                return l
        return None

    def retrato(l, por_que):
        if not l:
            return None
        return {'VIDEO_ID': l['VIDEO_ID'], 'SOURCE_URL': l['SOURCE_URL'],
                'TITLE': l['TITLE'], 'TEXT_SOURCE': l['TEXT_SOURCE'],
                'CAPTION_STATE': l['CAPTION_STATE'], 'WHISPER_STATE': l['WHISPER_STATE'],
                'DE': l['TITLE_ONLY']['CONTENT_TYPE'],
                'PARA': l['CAPTION_OR_WHISPER']['CONTENT_TYPE'],
                'TEXT_CHARS_GANHOS': l['TEXT_CHARS_GANHOS'],
                'POR_QUE': por_que}

    mudou = achar(lambda l: l['MUDOU'] and l['TEXT_CHARS_GANHOS'] > 0)
    confirmou = achar(lambda l: not l['MUDOU'] and l['TEXT_CHARS_GANHOS'] > 0)
    campo = achar(lambda l: l['CAPTION_OR_WHISPER']['FIELD_SIGNAL']
                  and not l['TITLE_ONLY']['FIELD_SIGNAL'])
    ainda = achar(lambda l: l['CAPTION_OR_WHISPER']['NAO_SEI'])
    falso = achar(lambda l: l['TITLE_ONLY']['OFF_TOPIC']
                  and not l['CAPTION_OR_WHISPER']['OFF_TOPIC'])
    return {
        'MUDOU_UMA_CLASSIFICACAO': retrato(
            mudou, 'o texto a mais mudou o tipo de %s para %s'
            % (mudou['TITLE_ONLY']['CONTENT_TYPE'],
               mudou['CAPTION_OR_WHISPER']['CONTENT_TYPE']) if mudou else ''),
        'CONFIRMOU_UMA_CLASSIFICACAO': retrato(
            confirmou, 'o texto a mais chegou e o tipo NÃO mudou — confirmação custa o '
                       'mesmo que surpresa, e vale tanto quanto'),
        'REVELOU_UM_FIELD_SIGNAL': retrato(
            campo, 'só com o texto a mais apareceu relato de campo'),
        'CONTINUOU_NAO_SEI': retrato(
            ainda, 'nem legenda nem whisper deram texto suficiente — e o estado diz de '
                   'qual dos dois faltou'),
        'EVITOU_FALSO_OFF_TOPIC': retrato(
            falso, 'pelo título seria descartado; com o texto a mais, não é'),
    }


# ═══════════════════════════════════════════════════════════════════ A RODADA

def rodar(pular_legendas=False):
    """legenda (dono canônico) → escada → segunda escada (cache) → medição. → 0/1."""
    escolhidos, diario = escolher()
    if not escolhidos:
        for d in diario:
            print('  %s' % d)
        return 1
    ids = [i['VIDEO_ID'] for i in escolhidos]
    for d in diario:
        print('  %s' % d)
    print()

    if not pular_legendas:
        print('── DEGRAU 2 · a legenda, pelo dono dela ' + '─' * 34)
        try:
            yj.fase_legendas(ids=ids)
        except Exception as e:                                 # noqa: BLE001
            # A fase de legenda depende do navegador desta máquina. Se ela cair, o teste
            # NÃO vira "estes vídeos não têm legenda": vira CAPTION_NOT_TESTED, e a
            # escada se recusa a rodar o whisper — que é o desenho.
            print('  ⚠️  a fase de legenda caiu: %s: %s' % (type(e).__name__, str(e)[:160]))
            print('      isto NÃO diz que os vídeos não têm legenda.')
        print()

    print('── DEGRAUS 3 a 5 · a escada ' + '─' * 46)
    t0 = time.time()
    yt.escada(ids=ids)
    primeira = time.time() - t0
    print()

    print('── A SEGUNDA EXECUÇÃO, QUE TEM DE USAR O CACHE ' + '─' * 27)
    t0 = time.time()
    yt.escada(ids=ids)
    segunda = time.time() - t0
    print('  primeira execução: %.1f s · segunda: %.1f s' % (primeira, segunda))
    print()

    print('── A MEDIÇÃO ' + '─' * 61)
    return medir()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'escolher'
    if cmd == 'escolher':
        raise SystemExit(fase_escolher())
    if cmd == 'medir':
        raise SystemExit(medir())
    if cmd in ('rodar', 'tudo'):
        raise SystemExit(rodar(pular_legendas='--sem-legendas' in sys.argv))
    print('uso: youtube_microteste.py {escolher|rodar [--sem-legendas]|medir|tudo}')
    raise SystemExit(2)
