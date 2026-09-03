#!/usr/bin/env python3
"""
VALE A PENA ESTA FONTE? — a peneira que roda ANTES do whisper, e custa zero.

    py scripts/youtube_relevancia.py fontes    # o canal fala a língua do projeto?
    py scripts/youtube_relevancia.py fila      # quem vai ao whisper, e por quê
    py scripts/youtube_relevancia.py teste     # as provas, sem rede
    py scripts/youtube_relevancia.py tudo

POR QUE ESTE ARQUIVO EXISTE
=============================
`instagram_transcrever.py` mediu `small` a 3,2x nesta máquina: mil vídeos são ~6 h.
Transcrever tudo é gastar seis horas para descobrir depois o que era vinheta de marca.

    O WHISPER NÃO É CARO POR DÓLAR. ELE É CARO POR HORA DE MÁQUINA,
    E HORA DE MÁQUINA GASTA NA ORDEM EM QUE A FILA MANDA.

Este arquivo não coleta, não transcreve e não grava fora do diretório dele. Ele mede
e ordena — quem executa é `youtube_transcrever.py`, que obedece a fila daqui.

O QUE ESTA CASA APRENDEU COM O REPOSITÓRIO DO BRASIL
======================================================
`relevancia-de-fonte.py` do `portal-sintonia` já pagou por estas regras, e elas
entram aqui pelo mesmo motivo que lá:

  1. **Texto curto vira `talvez`, NUNCA `nao_fala`.** A bio *"Eng. Agr. Dr. em
     Fitopatologia — Embrapa"* — 6 palavras, um fitopatologista de verdade — saía
     `nao_fala`, o veredito mais forte do arquivo, porque a pergunta dos achados
     vinha antes do piso de palavras.

         É DECLARAR QUE A PESSOA NÃO FALA INGLÊS DEPOIS DE OUVIR ELA DIZER "OI".

     Aqui isso importa ainda mais: o texto livre de um vídeo é o TÍTULO, e título
     tem sete palavras. Nenhuma recusa deste arquivo pode se apoiar num título.

  2. **Contagem não distingue sentido.** Lá, `resistencia` entrou com 129 documentos
     e 105 pessoas, e metade era lona de caçamba e suspensão de trator. Aqui a
     tradução é `Curso natural del agua` virando `TECHNICAL_WEBINAR` — o defeito que
     `sensor_medir.py` já registra na própria docstring.

  3. **Uma palavra sozinha não é vocabulário.** Se um termo é mais de 70% dos
     achados, aquilo é um assunto repetido.

  4. **A régua ausente é falta de régua, não veredito sobre a fonte.**

O LÉXICO NÃO É MEU, E ISSO É A REGRA MAIS IMPORTANTE DAQUI
============================================================
Ele é importado de `sensor_medir.py`, que é onde esta casa declara o vocabulário
multilíngue (ES/IT/FR) e onde ele é mantido. Copiar os termos para cá criaria uma
segunda régua que mede menos amanhã e não avisa — foi assim que o `_ler-fonte.py` do
Brasil ficou com 6 termos chumbados enquanto o radar já tinha 29.

    DICIONÁRIO COPIADO É DICIONÁRIO QUE ENVELHECE EM SILÊNCIO.

OS LIMIARES SAEM DO PRÓPRIO QUADRO
====================================
O piso de duração NÃO é um número escolhido a dedo. Ele é a mediana da duração do
próprio canal dividida por quatro — a mesma ideia do `limiar_conflacao` do `filas.py`,
que tira o teto de organizações da mediana do quadro em vez de arbitrar 10.

Um canal de vídeos de 4 minutos e um de vídeos de 40 segundos não podem ser medidos
pelo mesmo piso, e nenhum dos dois deveria ser medido por um piso que eu inventei.
"""
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sensor_medir as sm        # noqa: E402  — dono do léxico multilíngue desta casa

SAMPLES = os.path.join(ROOT, 'data', 'samples')
JANELA = os.path.join(SAMPLES, 'YOUTUBE-JANELA')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-RELEVANCIA')
NAO_SEI = 'NOT_KNOWN'
MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'

# ── OS LIMIARES DO VEREDITO, VINDOS DO `relevancia-de-fonte.py` DO BRASIL ──────
# Eles são de lá, com os nomes de lá, para que quem conhecer um reconheça o outro.
PISO_PALAVRAS = 40      # abaixo disto, densidade é razão sem denominador
ALVO_DISTINTAS = 3      # termos distintos e sem ressalva para `fala_a_lingua`
ALVO_DENSIDADE = 4.0    # achados por mil palavras
TETO_DE_UMA = 0.70      # nenhum termo sozinho pode valer mais que isto

# ── ORÇAMENTO DE MÁQUINA ──────────────────────────────────────────────────────
# 3,2x é MEDIDO, não estimado: `instagram_transcrever.py` cronometrou `small` nesta
# máquina, nos 16 núcleos, contra um reel de 110 s da @basf_agroes.
VELOCIDADE_SMALL = 3.2
ORCAMENTO_H = float(os.environ.get('YT_ORCAMENTO_H') or 2.0)


def agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoje():
    import datetime
    return datetime.date.today().isoformat()


def _ler(nome):
    p = os.path.join(JANELA, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/YOUTUBE-RELEVANCIA/' + nome


def normaliza(t):
    """Sem acento, minúsculo. O léxico do `sensor_medir` é escrito assim."""
    t = unicodedata.normalize('NFD', str(t or '').lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', t)


# ══════════════════════════════════════════════ O DICIONÁRIO, LIDO DO DONO DELE

# Termos que medem DUAS coisas e por isso não promovem veredito sozinhos — a
# tradução da `ressalva` do Brasil. `curso` é o caso que esta casa já mediu:
# `Curso natural del agua` virou `TECHNICAL_WEBINAR`.
COM_RESSALVA = {'curso', 'accion', 'azione', 'action', 'campo', 'programa del',
                'programma del', 'webinar', 'seminario'}


def dicionario():
    """Os termos, LIDOS AGORA das DUAS metades. → {termo_normalizado: categoria}

    ⚠️ NÃO COPIE O RESULTADO DISTO PARA DENTRO DE CÓDIGO. O dono da primeira metade
    é o `sensor_medir.py`; o da segunda é o arquivo dos aprovados. Este arquivo é
    inquilino dos dois. Cópia feita hoje mede menos amanhã e não avisa — foi assim
    que o `_ler-fonte.py` do Brasil ficou com 6 termos enquanto o radar tinha 29.

    METADE 1 · `sensor_medir.py`, frases de FALA, para comentário e transcrição.
    METADE 2 · `LEXICO-APROVADO.json`, termos de TÍTULO, aprovados por gente.

    A segunda existe porque a primeira cobriu 5% dos títulos do lote em 2026-09-03.
    """
    d = {}
    for cat in ('OBSERVACAO_CAMPO', 'PESQUISA', 'INTERPRETACAO', 'EVENTO',
                'MARKETING', 'NOTICIA', 'PRIMEIRA_PESSOA'):
        for termo in getattr(sm, cat, []):
            n = normaliza(termo)
            if len(n) >= 4:
                d[n] = cat
    ap = os.path.join(SAIDA, 'LEXICO-APROVADO.json')
    if os.path.exists(ap):
        with open(ap, encoding='utf-8') as f:
            for t in (json.load(f).get('TERMOS') or []):
                n = normaliza(t.get('TERMO', ''))
                cat = t.get('CATEGORIA')
                if len(n) >= 4 and cat:
                    d[n] = cat
                    if t.get('RESSALVA'):
                        COM_RESSALVA.add(n)
    return d


# `EVENTO`, `MARKETING` e `NOTICIA` dizem que o canal fala de agro — mas dizem
# também que ESTE material é convite, propaganda ou release. Eles contam para a
# FONTE e pesam contra o VÍDEO. Duas perguntas diferentes, dois usos do mesmo termo.
CATEGORIAS_TECNICAS = {'OBSERVACAO_CAMPO', 'PESQUISA', 'INTERPRETACAO', 'PRIMEIRA_PESSOA'}
CATEGORIAS_PROMOCIONAIS = {'EVENTO', 'MARKETING', 'NOTICIA'}


def varre(texto, dic):
    """→ (achados_por_termo, n_palavras). Só isso: contar é diferente de julgar."""
    n = normaliza(texto)
    palavras = len([p for p in n.split(' ') if p])
    achados = {}
    for termo in dic:
        c = n.count(termo)
        if c:
            achados[termo] = c
    return achados, palavras


def veredito(achados, n_palavras, dic):
    """A regra, sozinha numa função, para a prova poder chamá-LA e não uma cópia.

    A lição é do `diario.py` do Brasil: prova que copia os `if` para dentro de si
    confere uma cópia da regra e continua verde depois que a regra muda. *É conferir
    a chave contra uma foto da chave.*
    """
    if n_palavras == 0:
        return 'nao_fala', ('não veio texto para medir — isto NÃO é evidência sobre '
                            'a fonte, é a falta dela')
    # ⚠️ O PISO VEM ANTES DA PERGUNTA DOS ACHADOS. A ORDEM ERA O DEFEITO, LÁ E AQUI.
    if n_palavras < PISO_PALAVRAS:
        return 'talvez', ('só %d palavras de texto — abaixo de %d a densidade é razão '
                          'sem denominador. Vale para quem achou termo E para quem não '
                          'achou: texto curto não é "foi lido e não tinha"'
                          % (n_palavras, PISO_PALAVRAS))
    if not achados:
        return 'nao_fala', ('nenhum termo do léxico aparece em %d palavras de texto'
                            % n_palavras)
    limpos = [t for t in achados if t not in COM_RESSALVA]
    total = sum(achados.values())
    if not limpos:
        return 'talvez', ('os únicos achados são termos COM RESSALVA — eles medem duas '
                          'coisas e sozinhos não provam agronomia')
    if len(limpos) < ALVO_DISTINTAS:
        return 'talvez', ('%d termo(s) distinto(s) sem ressalva, e o piso é %d: '
                          'um assunto não é uma língua' % (len(limpos), ALVO_DISTINTAS))
    maior = max(achados.values()) / total
    if maior > TETO_DE_UMA:
        return 'talvez', ('um termo sozinho é %.0f%% dos achados (teto %.0f%%) — isso '
                          'é um assunto repetido, não vocabulário'
                          % (maior * 100, TETO_DE_UMA * 100))
    dens = sum(achados[t] for t in limpos) / n_palavras * 1000
    if dens < ALVO_DENSIDADE:
        return 'talvez', ('densidade %.1f por mil, abaixo de %.1f: os termos estão lá, '
                          'diluídos demais' % (dens, ALVO_DENSIDADE))
    return 'fala_a_lingua', ('%d termos distintos sem ressalva, %.1f por mil palavras'
                             % (len(limpos), dens))


# ── TIPO DE CORPUS ────────────────────────────────────────────────────────────
# Um corpus feito só de TÍTULOS não pode sustentar `nao_fala`, e isto foi MEDIDO:
# em 2026-09-03, contra o lote real, `SyngentaFrance` saiu `nao_fala` com 375
# palavras de título. Os títulos dela são:
#
#     "JTCM - La qualité du blé français est-elle au rendez-vous ?"
#     "Le pouvoir couvrant des orges HYVIDO® : démonstration en parcelle !"
#
# Isso é agronomia sem nenhuma dúvida. O que faltou não foi o assunto: foi o TIPO
# de texto. O léxico do `sensor_medir` é feito de frases de FALA — "hemos
# observado", "nuestro estudio", "abbiamo rilevato" — porque nasceu para medir
# comentário e transcrição. Nenhum título do mundo diz "hemos observado".
#
#     TEXTO CURTO NÃO SUSTENTA `nao_fala`. TEXTO DO TIPO ERRADO TAMBÉM NÃO.
#
# É a mesma lei do piso de palavras do Brasil, um passo adiante: lá o problema era
# a QUANTIDADE, aqui é a NATUREZA. Nos dois casos o estrago seria o mesmo — carimbar
# a fonte certa com o veredito mais forte do arquivo.
CORPUS_FRACO = 'TITULOS_E_DESCRICAO'
CORPUS_FORTE = 'COM_LEGENDA'


def ajusta_por_corpus(v, motivo, corpus_tipo):
    """`nao_fala` só vale sobre corpus FORTE. → (veredito, motivo)

    Mora separada de `veredito()` de propósito: a prova precisa poder chamar as duas,
    e a regra do corpus é uma decisão diferente da regra do vocabulário.
    """
    if v == 'nao_fala' and corpus_tipo != CORPUS_FORTE:
        return 'talvez', (
            'o léxico não achou nada, e o corpus é %s — título não contém as frases de '
            'fala que este léxico procura ("hemos observado", "nuestro estudio"). Isto é '
            'limite da RÉGUA sobre este corpus, não veredito sobre a fonte. Rode '
            '`legendas` e meça de novo.' % corpus_tipo)
    return v, motivo


# ══════════════════════════════════════════════════════════ CAMADA 1 · A FONTE

def fase_fontes():
    canais, objetos = _ler('CANAIS.json'), _ler('OBJETOS.json')
    if not canais or not objetos:
        print('faltam CANAIS.json/OBJETOS.json — rode `youtube_janela.py tudo` antes')
        return 1
    dic = dicionario()
    por_canal = {}
    for v in objetos['ITEMS']:
        por_canal.setdefault(v.get('ACCOUNT_HANDLE'), []).append(v)

    # A legenda, quando existe, é o corpus de VERDADE: é fala, que é o que este léxico
    # sabe medir. Enquanto ela não existir, o veredito é sobre título — e
    # `ajusta_por_corpus` impede que isso vire recusa.
    legendas, fala_por_canal = _ler('LEGENDAS.json'), {}
    if legendas:
        for l in legendas['ITEMS']:
            if l.get('CAPTION_STATE') != 'PRESENTE':
                continue
            txt = ' '.join(t['TEXTO'] for t in (l.get('TRANSCRICAO') or []))
            if txt:
                fala_por_canal.setdefault(l.get('ACCOUNT_HANDLE'), []).append(txt)

    fontes = []
    for c in canais['CANAIS']:
        h = c.get('ACCOUNT_HANDLE')
        vids = por_canal.get(h, [])
        # O corpus da FONTE é a descrição do canal MAIS todos os títulos dele. Um
        # título sozinho não sustenta veredito; oitenta títulos sustentam.
        desc = c.get('DESCRIPTION') if c.get('DESCRIPTION') != NAO_SEI else ''
        fala = fala_por_canal.get(h) or []
        corpus_tipo = CORPUS_FORTE if fala else CORPUS_FRACO
        corpus = ' '.join([desc or ''] + [str(v.get('TITLE') or '') for v in vids] + fala)
        achados, n = varre(corpus, dic)
        v_, motivo = veredito(achados, n, dic)
        v_, motivo = ajusta_por_corpus(v_, motivo, corpus_tipo)
        fontes.append({
            'ACCOUNT_HANDLE': h,
            'COMPANY': c.get('COMPANY'),
            'COUNTRY_SCOPE': c.get('COUNTRY_SCOPE'),
            'SUBSCRIBERS': c.get('SUBSCRIBERS', NAO_SEI),
            'SUBSCRIBERS_EXATO': c.get('SUBSCRIBERS_EXATO', False),
            'VIDEOS_LIDOS': len(vids),
            'PALAVRAS_DO_CORPUS': n,
            'CORPUS_E': ('descrição do canal + títulos'
                         + (' + %d legenda(s)' % len(fala) if fala else '')),
            'CORPUS_TIPO': corpus_tipo,
            'VIDEOS_COM_LEGENDA_NO_CORPUS': len(fala),
            'ACHADOS': achados,
            'ACHADOS_DISTINTOS': len(achados),
            'ACHADOS_SEM_RESSALVA': len([t for t in achados if t not in COM_RESSALVA]),
            'VEREDITO': v_,
            'POR_QUE': motivo,
        })
        print('  %-24s %-14s %-4s palavras  %s'
              % (str(h)[:24], v_, n, motivo[:58]))

    p = _gravar('FONTES.json', {
        'SOURCE_ID': 'YOUTUBE-RELEVANCIA/FONTES',
        'source': 'derivado de YOUTUBE-JANELA — nenhuma coleta, nenhum custo',
        'SOURCE_LOCATION': 'derivado — interno',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_E': ('a pergunta "esta fonte fala a língua do projeto?", medida '
                         'sobre a descrição do canal mais os títulos dele. NÃO é a '
                         'decisão de transcrever: é o guarda que vem antes dela.'),
        'DE_ONDE_VEM_O_LEXICO': ('scripts/sensor_medir.py, lido em tempo de execução. '
                                 'Copiar os termos para cá criaria uma segunda régua.'),
        'REGRA_DO_VEREDITO': ('portada de relevancia-de-fonte.py do portal-sintonia: '
                              'piso de %d palavras ANTES da pergunta dos achados, %d '
                              'termos distintos sem ressalva, teto de %.0f%% para um '
                              'termo só, densidade mínima de %.1f por mil.'
                              % (PISO_PALAVRAS, ALVO_DISTINTAS, TETO_DE_UMA * 100,
                                 ALVO_DENSIDADE)),
        'LIMITE_DECLARADO': ('o classificador é LEXICAL. `Curso natural del agua` já '
                             'virou TECHNICAL_WEBINAR nesta casa. Cobertura alta aqui '
                             'é suspeita, não conquista — a verificação é humana.'),
        'FONTES': fontes})
    print('gravado: %s' % p)
    return 0


# ═══════════════════════════════════════════════════════════ CAMADA 2 · A FILA

def piso_de_duracao(duracoes):
    """O piso sai da MEDIANA DO PRÓPRIO CANAL, não de um número escolhido a dedo.

    Mesma ideia do `limiar_conflacao` do `filas.py`, que tira o teto de organizações
    da mediana do quadro em vez de arbitrar 10. Um canal de vídeos de 4 minutos e um
    de vídeos de 40 segundos não podem dividir o mesmo piso.
    """
    n = [d for d in duracoes if isinstance(d, int) and d > 0]
    if not n:
        return None
    return max(15, int(statistics.median(n) / 4))


def fase_fila():
    objetos, fontes = _ler('OBJETOS.json'), None
    p = os.path.join(SAIDA, 'FONTES.json')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            fontes = json.load(f)
    if not objetos or not fontes:
        print('faltam OBJETOS.json/FONTES.json — rode `fontes` antes')
        return 1

    legendas = _ler('LEGENDAS.json')
    estado_por_video = {}
    if legendas:
        for l in legendas['ITEMS']:
            estado_por_video[l['VIDEO_ID']] = l.get('CAPTION_STATE')

    vered = {f['ACCOUNT_HANDLE']: f['VEREDITO'] for f in fontes['FONTES']}
    dic = dicionario()
    por_canal = {}
    for v in objetos['ITEMS']:
        por_canal.setdefault(v.get('ACCOUNT_HANDLE'), []).append(v)
    pisos = {h: piso_de_duracao([x.get('DURATION_S') for x in vs])
             for h, vs in por_canal.items()}

    fila, recusados, motivos = [], [], {}
    for v in objetos['ITEMS']:
        h = v.get('ACCOUNT_HANDLE')
        dur = v.get('DURATION_S')
        estado = estado_por_video.get(v['VIDEO_ID'], 'NOT_TESTED')
        achados, n_pal = varre(v.get('TITLE') or '', dic)
        tecnicos = [t for t in achados if dic[t] in CATEGORIAS_TECNICAS]
        promo = [t for t in achados if dic[t] in CATEGORIAS_PROMOCIONAIS]

        item = {
            'VIDEO_ID': v['VIDEO_ID'], 'ACCOUNT_HANDLE': h,
            'TITLE': v.get('TITLE'), 'DURATION_S': dur,
            'VIEWS': v.get('VIEWS'), 'PUBLISHED_RELATIVE': v.get('PUBLISHED_RELATIVE'),
            'CAPTION_STATE': estado,
            'FONTE_VEREDITO': vered.get(h, NAO_SEI),
            'TERMOS_TECNICOS_NO_TITULO': tecnicos,
            'TERMOS_PROMOCIONAIS_NO_TITULO': promo,
        }
        recusa = None
        if estado == 'PRESENTE':
            recusa = 'JA_TEM_LEGENDA'
        elif estado == 'NOT_TESTED':
            recusa = 'LEGENDA_NAO_TESTADA'
        elif vered.get(h) == 'nao_fala':
            # Só chega aqui quem foi medido sobre corpus FORTE: `ajusta_por_corpus` já
            # converteu em `talvez` todo `nao_fala` tirado de título.
            recusa = 'FONTE_NAO_FALA_A_LINGUA'
        elif not isinstance(dur, int):
            recusa = 'SEM_DURACAO_LEGIVEL'
        elif pisos.get(h) and dur < pisos[h]:
            recusa = 'CURTO_PARA_O_PROPRIO_CANAL'

        if recusa:
            item['DECISAO'] = 'FORA'
            item['POR_QUE'] = {
                'JA_TEM_LEGENDA': ('o YouTube já entregou o texto de graça. Transcrever '
                                   'seria pagar hora de máquina por algo que existe escrito.'),
                'LEGENDA_NAO_TESTADA': ('a camada `legendas` ainda não rodou sobre este '
                                        'vídeo. Isto NÃO diz que ele não tem legenda — '
                                        'diz que ninguém perguntou.'),
                'FONTE_NAO_FALA_A_LINGUA': ('o canal inteiro não passou no guarda de '
                                            'vocabulário. A recusa é da FONTE, não deste vídeo.'),
                'SEM_DURACAO_LEGIVEL': ('sem duração não há como estimar o custo de '
                                        'máquina, e fila sem custo não é orçamento.'),
                'CURTO_PARA_O_PROPRIO_CANAL': ('%s s, abaixo do piso de %s s deste canal '
                                               '(mediana/4). Vinheta e bumper falam pouco.'
                                               % (dur, pisos.get(h))),
            }[recusa]
            item['MOTIVO'] = recusa
            motivos[recusa] = motivos.get(recusa, 0) + 1
            recusados.append(item)
            continue

        item['CUSTO_DE_MAQUINA_S'] = round(dur / VELOCIDADE_SMALL, 1)
        item['DECISAO'] = 'ELEGIVEL'
        fila.append(item)

    # ── A ORDENAÇÃO, DECLARADA ────────────────────────────────────────────────
    # Ela é PRIORIDADE, não afirmação sobre o conteúdo. Um título com termo técnico
    # não prova que o vídeo é técnico — prova que ele merece ser ouvido antes.
    def chave(i):
        v = i.get('VIEWS')
        return (-len(i['TERMOS_TECNICOS_NO_TITULO']),
                len(i['TERMOS_PROMOCIONAIS_NO_TITULO']),
                -(v if isinstance(v, int) else -1),
                i.get('CUSTO_DE_MAQUINA_S', 0))
    fila.sort(key=chave)

    orcamento_s = ORCAMENTO_H * 3600
    gasto, dentro, fora_orcamento = 0.0, [], []
    for i in fila:
        if gasto + i['CUSTO_DE_MAQUINA_S'] <= orcamento_s:
            gasto += i['CUSTO_DE_MAQUINA_S']
            i['DECISAO'] = 'NA_FILA'
            dentro.append(i)
        else:
            i['DECISAO'] = 'FORA_DO_ORCAMENTO'
            i['POR_QUE'] = ('elegível, e o orçamento de %.1f h acabou antes dele. Isto '
                            'NÃO é recusa: é ordem. Aumente YT_ORCAMENTO_H e ele entra.'
                            % ORCAMENTO_H)
            fora_orcamento.append(i)

    # QUAL CRITÉRIO REALMENTE FILTRA — o campo que denuncia critério decorativo.
    qual = (max(motivos.items(), key=lambda x: x[1]) if motivos else (None, 0))
    p = _gravar('FILA-WHISPER.json', {
        'SOURCE_ID': 'YOUTUBE-RELEVANCIA/FILA-WHISPER',
        'source': 'derivado de YOUTUBE-JANELA e YOUTUBE-RELEVANCIA/FONTES — sem custo',
        'SOURCE_LOCATION': 'derivado — interno',
        'FACT_LOCATION': 'EAME', 'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ESTA_FILA_E': ('a lista de vídeos que vão ao whisper local, e a ordem. '
                              'Não é a transcrição: é a decisão de gastar hora de '
                              'máquina, tomada antes de gastá-la.'),
        'ORDENACAO_DECLARADA': ('mais termos técnicos no título, depois menos termos '
                                'promocionais, depois mais visualizações, depois mais '
                                'barato de transcrever'),
        'A_ORDENACAO_NAO_AFIRMA': ('título com termo técnico não prova vídeo técnico. '
                                   'A ordem diz quem é ouvido antes, não quem é bom.'),
        'ORCAMENTO_H': ORCAMENTO_H,
        'VELOCIDADE_MEDIDA': ('%.1fx para o modelo `small`, cronometrado por '
                              'instagram_transcrever.py nesta máquina' % VELOCIDADE_SMALL),
        'UNIVERSO': len(objetos['ITEMS']),
        'ELEGIVEIS': len(fila),
        'NA_FILA': len(dentro),
        'FORA_DO_ORCAMENTO': len(fora_orcamento),
        'RECUSADOS': len(recusados),
        'MOTIVOS_DE_RECUSA': motivos,
        'QUAL_CRITERIO_REALMENTE_FILTRA': (
            'nenhum: nada foi recusado' if not qual[0] else
            '%s, com %d dos %d recusados. Os outros critérios são GUARDA, não peneira '
            '— e um critério que nunca recusa ninguém precisa ser dito, não escondido.'
            % (qual[0], qual[1], len(recusados))),
        'CUSTO_DE_MAQUINA_DA_FILA_S': round(gasto, 1),
        'CUSTO_DE_MAQUINA_DA_FILA_H': round(gasto / 3600, 2),
        'QUEUE': dentro,
        'FORA_DO_ORCAMENTO_ITENS': fora_orcamento,
        'RECUSADOS_ITENS': recusados})
    print('universo=%d  elegiveis=%d  na_fila=%d  fora_do_orcamento=%d  recusados=%d'
          % (len(objetos['ITEMS']), len(fila), len(dentro), len(fora_orcamento),
             len(recusados)))
    for m, c in sorted(motivos.items(), key=lambda x: -x[1]):
        print('   recusa: %-30s %d' % (m, c))
    print('custo de maquina da fila: %.2f h (orcamento %.1f h)' % (gasto / 3600, ORCAMENTO_H))
    print('gravado: %s' % p)
    return 0


# ══════════════════════════════════════════════════════ CALIBRAÇÃO DO LÉXICO
#
# ⚠️ PEDIDO DO LUCIANO EM 2026-09-03: *"talvez as palavras do brasil nao sejam as
# mesmas pra italia, precisa calibrar isso, talvez aumentar o leque de palavras"*.
#
# A medição de hoje diz que ele está certo, e diz mais do que ele pediu: o problema
# não é só a Itália. Contra o lote real, 375 palavras de título francês da Syngenta
# France — `La qualité du blé français`, `orges HYVIDO® : démonstration en parcelle`
# — deram ZERO achados. O léxico do `sensor_medir` nasceu para medir COMENTÁRIO e
# TRANSCRIÇÃO, e é feito de frases de fala: `hemos observado`, `abbiamo rilevato`.
# Nenhum título do mundo diz "hemos observado".
#
# O QUE ESTE BLOCO FAZ, E O QUE ELE SE RECUSA A FAZER
# -----------------------------------------------------
# Faz: mede a cobertura do léxico de hoje, e PROPÕE candidatos tirados do corpus
# real, com a evidência de cada um ao lado.
#
# NÃO faz: aprovar sozinho. Termo proposto nasce `PROPOSTO_NAO_APROVADO` e não entra
# em veredito nenhum enquanto uma pessoa não o mover para o arquivo dos aprovados.
# É a lição do `aprender.py` do Brasil ao contrário — lá o voto humano é o gabarito
# que suprime; aqui é o gabarito que admite.
#
#     LÉXICO QUE CRESCE SOZINHO MEDE O QUE ELE MESMO INVENTOU.
#
# O DISCRIMINADOR É ESPALHAMENTO, NÃO FREQUÊNCIA
# ------------------------------------------------
# Um termo que aparece muito num canal só é o jargão daquele canal — `HYVIDO` é
# marca da Syngenta, não a língua do projeto. Por isso o candidato precisa aparecer
# em pelo menos DOIS canais independentes.
#
# É a mesma lição de `aprender-caca.py`: *"o termo que achou o agrônomo achou o
# cachaceiro também"*. Um termo só prova que é língua comum quando fontes que não
# combinaram entre si usam ele.

# Palavras de função dos quatro idiomas do lote. Isto é uma APOSTA DECLARADA, no
# mesmo espírito do `sensor_medir`: não é verdade linguística, é uma lista que
# alguém escreveu e que pode ser conferida e corrigida.
VAZIAS = set("""
de da do das dos la el los las un una uno unos unas y o e a en con por para del al se
su sus que es son ser esta este estas estos como mas pero no si lo le les nos te me mi
tu ya muy todo todos toda todas otro otra cada donde cuando porque sobre entre desde
il lo gli le dei delle degli della dello dell nel nella nello nelle negli sul sulla
sullo sulle sugli dal dalla dallo dalle dagli alla allo alle agli con per tra fra non
piu sono essere questo questa questi queste come ma anche solo quando dove perche
tutto tutti tutta tutte molto ogni altro altra altri altre fare puo gia senza cosa
ecco parte prima dopo anno anni nuovo nuova nuovi nuove qui quello quella
les des aux dans sur pour par avec sans sous vers chez est sont etre cette ces ils
son ses leur leurs qui que quoi dont ou mais donc car ne pas plus tres tout tous toute
toutes autre autres faire peut deja comme quand ainsi apres avant nouveau nouvelle
the and for with from this that are was were you your our their its has have not but
all any can more other new about into over than then them they what when where which
video videos canale canal channel youtube shorts short live puntata episodio
www http https com net org
""".split())

# Espalhamento mínimo: em quantos canais diferentes o termo precisa aparecer.
ESPALHAMENTO_MINIMO = 2
# Tamanho mínimo, herdado do PISO_LETRAS do Brasil.
PISO_LETRAS = 4


def _palavras(texto):
    return [p for p in re.split(r'[^0-9a-zà-ÿ®]+', normaliza(texto)) if p]


def fase_calibrar():
    canais, objetos = _ler('CANAIS.json'), _ler('OBJETOS.json')
    if not canais or not objetos:
        print('faltam CANAIS.json/OBJETOS.json — rode `youtube_janela.py tudo` antes')
        return 1
    dic = dicionario()

    por_canal = {}
    for v in objetos['ITEMS']:
        por_canal.setdefault(v.get('ACCOUNT_HANDLE'), []).append(v)
    desc_por_canal = {c.get('ACCOUNT_HANDLE'):
                      (c.get('DESCRIPTION') if c.get('DESCRIPTION') != NAO_SEI else '')
                      for c in canais['CANAIS']}

    # ── 1. A COBERTURA DE HOJE, QUE É O DIAGNÓSTICO ───────────────────────────
    cobertura, titulos_tocados, titulos_totais = [], 0, 0
    for h, vids in por_canal.items():
        tocados = 0
        for v in vids:
            titulos_totais += 1
            a, _ = varre(v.get('TITLE') or '', dic)
            if a:
                tocados += 1
                titulos_tocados += 1
        cobertura.append({'ACCOUNT_HANDLE': h, 'VIDEOS': len(vids),
                          'TITULOS_COM_ACHADO': tocados,
                          'COBERTURA_PCT': round(tocados / len(vids) * 100, 1) if vids else 0})

    # ── 2. OS CANDIDATOS, TIRADOS DO CORPUS REAL ──────────────────────────────
    canais_do_termo, ocorrencias = {}, {}
    for h, vids in por_canal.items():
        texto = ' '.join([desc_por_canal.get(h) or ''] +
                         [str(v.get('TITLE') or '') for v in vids])
        vistos_aqui = set()
        for p in _palavras(texto):
            if len(p) < PISO_LETRAS or p in VAZIAS or p.isdigit():
                continue
            if p in dic:
                continue                      # já está no léxico: não é candidato
            ocorrencias[p] = ocorrencias.get(p, 0) + 1
            if p not in vistos_aqui:
                vistos_aqui.add(p)
                canais_do_termo[p] = canais_do_termo.get(p, 0) + 1

    candidatos = []
    for p, n_canais in canais_do_termo.items():
        if n_canais < ESPALHAMENTO_MINIMO:
            continue
        candidatos.append({
            'TERMO': p,
            'CANAIS_EM_QUE_APARECE': n_canais,
            'OCORRENCIAS': ocorrencias[p],
            'ESTADO': 'PROPOSTO_NAO_APROVADO',
            'POR_QUE_PROPOSTO': ('aparece em %d canais independentes do lote, %d vezes '
                                 'no total' % (n_canais, ocorrencias[p])),
            'O_QUE_ISTO_NAO_PROVA': ('que o termo é técnico. Espalhamento prova que é '
                                     'língua COMUM entre as fontes, não que é agronomia. '
                                     'Quem decide isso é gente.'),
        })
    candidatos.sort(key=lambda c: (-c['CANAIS_EM_QUE_APARECE'], -c['OCORRENCIAS']))

    p1 = _gravar('LEXICO-COBERTURA.json', {
        'SOURCE_ID': 'YOUTUBE-RELEVANCIA/LEXICO-COBERTURA',
        'source': 'derivado de YOUTUBE-JANELA — nenhuma coleta, nenhum custo',
        'SOURCE_LOCATION': 'derivado — interno', 'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_E': ('quanto do corpus real o léxico de hoje toca. É o diagnóstico '
                         'que justifica calibrar — ou que dispensa.'),
        'TERMOS_NO_LEXICO': len(dic),
        'TITULOS_LIDOS': titulos_totais,
        'TITULOS_COM_ALGUM_ACHADO': titulos_tocados,
        'COBERTURA_GERAL_PCT': round(titulos_tocados / titulos_totais * 100, 1)
                               if titulos_totais else 0,
        'COMO_LER_ESTE_NUMERO': ('cobertura BAIXA sobre título não condena o léxico: ele '
                                 'foi feito para fala, e título não é fala. Cobertura '
                                 'ALTA seria suspeita, não conquista — é o que a '
                                 'docstring do sensor_medir já diz.'),
        'POR_CANAL': cobertura})

    p2 = _gravar('LEXICO-CANDIDATOS.json', {
        'SOURCE_ID': 'YOUTUBE-RELEVANCIA/LEXICO-CANDIDATOS',
        'source': 'derivado dos títulos e descrições já coletados — nenhuma coleta nova',
        'SOURCE_LOCATION': 'derivado — interno', 'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_E': ('candidatos a entrar no léxico, tirados do corpus REAL do lote. '
                         'Nenhum deles está em uso: todos nascem PROPOSTO_NAO_APROVADO.'),
        'COMO_APROVAR': ('mova o termo para LEXICO-APROVADO.json, na categoria certa, '
                         'com quem aprovou e quando. `dicionario()` lê os dois arquivos '
                         'em tempo de execução — nada é chumbado em código.'),
        'REGRA_DE_ENTRADA': ('aparecer em >= %d canais independentes, ter >= %d letras, '
                             'não ser palavra de função e não estar já no léxico'
                             % (ESPALHAMENTO_MINIMO, PISO_LETRAS)),
        'POR_QUE_ESPALHAMENTO_E_NAO_FREQUENCIA': (
            'termo que aparece muito num canal só é o jargão daquele canal — HYVIDO é '
            'marca da Syngenta, não a língua do projeto. É a lição do aprender-caca.py '
            'do Brasil: o termo que achou o agrônomo achou o cachaceiro também.'),
        'PALAVRAS_DE_FUNCAO_IGNORADAS': sorted(VAZIAS),
        'ESTA_LISTA_E_UMA_APOSTA': ('as palavras de função acima foram escritas à mão, '
                                    'nos quatro idiomas do lote. Não é verdade '
                                    'linguística: é lista conferível, e corrigível.'),
        'CANDIDATOS': len(candidatos),
        'ITENS': candidatos})

    print('léxico de hoje: %d termos · cobertura sobre título: %.1f%% (%d de %d)'
          % (len(dic), (titulos_tocados / titulos_totais * 100) if titulos_totais else 0,
             titulos_tocados, titulos_totais))
    print('candidatos propostos: %d (nenhum em uso)' % len(candidatos))
    print()
    print('  %-22s %-7s %s' % ('termo', 'canais', 'ocorrências'))
    for c in candidatos[:22]:
        print('  %-22s %-7s %s' % (c['TERMO'][:22], c['CANAIS_EM_QUE_APARECE'],
                                   c['OCORRENCIAS']))
    print()
    print('gravado: %s' % p1)
    print('gravado: %s' % p2)
    return 0


# ═══════════════════════════════════════════════════════════════════ AS PROVAS

def _testes():
    """Chamam `veredito()` DE VERDADE. Nada de `if` reimplementado aqui dentro."""
    dic = dicionario()
    falhas = []

    def diz(cond, oq, detalhe=''):
        print(('  OK   ' if cond else '  FALHA ') + oq + (' · ' + detalhe if detalhe else ''))
        if not cond:
            falhas.append(oq)

    # 1 · O DEFEITO QUE O BRASIL PAGOU: texto curto sem achados NÃO pode ser `nao_fala`.
    v, m = veredito({}, 6, dic)
    diz(v == 'talvez', 'texto de 6 palavras sem achados vira `talvez`, nao `nao_fala`', m[:56])

    # 2 · E texto curto COM achados também é `talvez` — o piso vale para os dois lados.
    v, m = veredito({'ensayo': 2}, 6, dic)
    diz(v == 'talvez', 'texto de 6 palavras COM achado tambem vira `talvez`', m[:56])

    # 3 · Texto longo sem nenhum achado é a única `nao_fala` legítima.
    v, m = veredito({}, 500, dic)
    diz(v == 'nao_fala', 'texto de 500 palavras sem nenhum achado vira `nao_fala`', m[:56])

    # 4 · Um termo dominando os achados é assunto repetido, não vocabulário.
    v, m = veredito({'ensayo': 95, 'observamos': 3, 'recomendamos': 2}, 500, dic)
    diz(v == 'talvez', 'um termo com 95% dos achados nao promove', m[:56])

    # 5 · Só termos com ressalva não promovem.
    v, m = veredito({'curso': 40, 'webinar': 30}, 500, dic)
    diz(v == 'talvez', 'so termos COM RESSALVA nao promovem', m[:56])

    # 6 · Vocabulário de verdade promove.
    v, m = veredito({'observamos': 12, 'el ensayo': 9, 'recomendamos': 8}, 500, dic)
    diz(v == 'fala_a_lingua', 'tres termos limpos e densos promovem', m[:56])

    # 7 · O piso de duração sai da mediana do canal, não de número fixo.
    diz(piso_de_duracao([200, 240, 260, 300]) == 62,
        'piso de duracao = mediana/4 do proprio canal', 'mediana 250 -> 62 s')
    diz(piso_de_duracao([20, 24, 28]) == 15,
        'canal de videos curtos nao herda piso de canal longo', 'piso minimo 15 s')
    diz(piso_de_duracao([]) is None, 'sem duracao legivel, sem piso inventado')

    # 8 · O DEFEITO MEDIDO EM 2026-09-03: corpus de titulo nao pode dizer `nao_fala`.
    v, m = ajusta_por_corpus('nao_fala', 'x', CORPUS_FRACO)
    diz(v == 'talvez', 'corpus de TITULO nao sustenta `nao_fala`', m[:56])

    # 9 · E sobre corpus FORTE ele continua valendo — senao a regra viraria anistia.
    v, m = ajusta_por_corpus('nao_fala', 'x', CORPUS_FORTE)
    diz(v == 'nao_fala', 'corpus COM LEGENDA continua podendo dizer `nao_fala`', m[:56])

    # 10 · A regra do corpus nao mexe em quem ja era `talvez` ou `fala_a_lingua`.
    diz(ajusta_por_corpus('fala_a_lingua', 'x', CORPUS_FRACO)[0] == 'fala_a_lingua',
        'a regra do corpus nao rebaixa quem passou')

    # 11 · O léxico vem do dono, e não está vazio.
    diz(len(dic) > 40, 'o lexico do sensor_medir chegou', '%d termos' % len(dic))

    print()
    print('FALHAS: %d' % len(falhas))
    return 1 if falhas else 0



# ══════════════════════════════════════════════ IDIOMA DOMINANTE DO TÍTULO
#
# ⚠️ MEDIDO EM 2026-09-03: DOS 397 CANAIS DO RECORTE "IT", SÓ 211 SÃO ITALIANOS.
# 87 são ingleses, 58 espanhóis, 39 sem marcador. `SAVER PAKISTAN`,
# `Willow Haven Farm`, `UNL CropWatch` e `KWS UK Ltd` estão dentro do recorte.
#
# A causa não é erro de coleta: `CASE_ID` com "IT" quer dizer RECORTE DE BUSCA
# italiano — a consulta foi feita com termo técnico em italiano. O YouTube
# respondeu com o mundo. Esta casa já escreveu a lei na direção normal:
#
#     IDIOMA != LUGAR.
#
# Aqui ela vale ao contrário: BUSCA EM ITALIANO != CANAL ITALIANO. Tratar os 397
# como italianos põe `farm`, `crop` e `control` no topo do léxico italiano — foi
# exatamente o que aconteceu na primeira calibração.
#
# ⚠️ O QUE ESTA MEDIÇÃO NÃO É
# Não é prova de país. É idioma do TÍTULO, e idioma continua não sendo lugar: um
# canal suíço em italiano sai IT aqui, e está certo para escolher vocabulário e
# errado para dizer onde a pessoa está. Para país, a prova é outra camada.
#
# A primeira versão desta medição errou e vale registrar: ela usou `con`, `una`,
# `del`, `como` como marcadores de espanhol — e os quatro existem em italiano.
# `AIPO verona` e `Infowine`, italianos, saíram classificados como espanhóis.
# Só marcador EXCLUSIVO entra nas listas abaixo.
MARCADORES = {
    'IT': set('della dello delle degli nella nello nelle negli sulla sullo dalla '
              'dagli gli anche perche piu tra sono questo quello quale come dei'.split()),
    'ES': set('los las para pero muy este esta donde cuando porque por hacia desde '
              'segun aqui aunque nuestro nuestra sus'.split()),
    'EN': set('the and for with from this that are was were your our their how what '
              'when which about have has been will'.split()),
    'FR': set('les des aux dans pour avec sans sous vers chez sont cette leur nous '
              'vous tout tous apres avant'.split()),
}
for _k in ('ES', 'EN', 'FR'):
    MARCADORES[_k] -= MARCADORES['IT']


def idioma_do_titulo(textos):
    """→ (idioma, contagens). SEM_MARCADOR quando nenhuma lista pontua."""
    pal = [p for t in textos for p in re.split(r'[^0-9a-zà-ÿ]+', normaliza(t)) if p]
    c = {k: sum(1 for p in pal if p in v) for k, v in MARCADORES.items()}
    topo = max(c.items(), key=lambda x: x[1])
    return ('SEM_MARCADOR' if topo[1] == 0 else topo[0]), c


def fase_idioma():
    canais, objetos = _ler('CANAIS.json'), _ler('OBJETOS.json')
    if not canais or not objetos:
        print('faltam CANAIS.json/OBJETOS.json'); return 1
    por = {}
    for v in objetos['ITEMS']:
        por.setdefault(v.get('ACCOUNT_HANDLE'), []).append(str(v.get('TITLE') or ''))
    itens, cont = [], {}
    for c in canais['CANAIS']:
        h = c.get('ACCOUNT_HANDLE')
        ts = por.get(h) or []
        idi, cs = idioma_do_titulo(ts + [c.get('DESCRIPTION') or ''])
        cont[idi] = cont.get(idi, 0) + 1
        itens.append({'ACCOUNT_HANDLE': h, 'TITLE_LANGUAGE_DOMINANT': idi,
                      'MARCADORES_POR_IDIOMA': cs, 'TITULOS_LIDOS': len(ts)})
    p = _gravar('CANAIS-IDIOMA.json', {
        'SOURCE_ID': 'YOUTUBE-RELEVANCIA/CANAIS-IDIOMA',
        'source': 'derivado dos títulos já coletados — nenhuma coleta nova, custo zero',
        'SOURCE_LOCATION': 'derivado — interno', 'FACT_LOCATION': 'ver por item',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'captured_at': hoje(), 'CAPTURED_AT': agora(), 'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_E': 'o idioma dominante do TÍTULO de cada canal, por marcador exclusivo',
        'O_QUE_ISTO_NAO_E': ('prova de país. IDIOMA != LUGAR: canal suíço em italiano '
                             'sai IT, e isso está certo para escolher vocabulário e '
                             'errado para dizer onde a pessoa está.'),
        'POR_QUE_EXISTE': ('o recorte que o acervo chama de "IT" é o RECORTE DE BUSCA, '
                           'não o canal. A busca foi em italiano; o YouTube respondeu '
                           'com o mundo. Sem este campo, `farm` e `crop` sobem ao topo '
                           'do léxico italiano — e foi o que aconteceu.'),
        'BY_LANGUAGE': cont, 'ITEMS': itens})
    print('idioma dominante do título, por canal:')
    for k, n in sorted(cont.items(), key=lambda x: -x[1]):
        print('   %-14s %3d' % (k, n))
    print('gravado: %s' % p)
    return 0



if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'fontes'
    if cmd == 'fontes':
        raise SystemExit(fase_fontes())
    if cmd == 'fila':
        raise SystemExit(fase_fila())
    if cmd == 'idioma':
        raise SystemExit(fase_idioma())
    if cmd == 'calibrar':
        raise SystemExit(fase_calibrar())
    if cmd == 'teste':
        raise SystemExit(_testes())
    if cmd == 'tudo':
        raise SystemExit(fase_fontes() or fase_fila())
    print('uso: youtube_relevancia.py {fontes|fila|idioma|calibrar|teste|tudo}')
    raise SystemExit(2)
