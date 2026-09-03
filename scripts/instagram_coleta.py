#!/usr/bin/env python3
"""
INSTAGRAM — o orquestrador. Uma fase por comando, um teto por fase, um manifesto por fase.

    py scripts/instagram_coleta.py contratos      # GRÁTIS · lê o schema de cada ator
    py scripts/instagram_coleta.py plano          # GRÁTIS · em que plano está cada chave
    py scripts/instagram_coleta.py janela         # GRÁTIS · a rota do navegador
    py scripts/instagram_coleta.py bio            # PAGA   · teste de fumaça de ~1 centavo
    py scripts/instagram_coleta.py posts          # PAGA   · um run por conta
    py scripts/instagram_coleta.py reels          # PAGA   · um run por conta
    py scripts/instagram_coleta.py comentarios    # PAGA   · atrás do portão de dado pessoal
    py scripts/instagram_coleta.py liquidar       # GRÁTIS · o custo REAL, depois
    py scripts/instagram_coleta.py semaforo       # GRÁTIS · a grade de cobertura

SEPARADO OU JUNTO? HÍBRIDO — E QUEM DECIDIU FOI O CONTRATO, NÃO O GOSTO
------------------------------------------------------------------------
Lido na Apify em 2026-09-02, nos builds vivos:

    apify~instagram-scraper 0.0.776   `resultsType` é STRING com enum
                                      ["posts","details","comments","reels","mentions",
                                      "stories"] — UM valor por execução, não lista.
    apify~instagram-profile-scraper   pede `usernames` (array)
    apify~instagram-reel-scraper      pede `username`  (array)
    scrapesmith~...-comments-scraper  pede `postUrls`  (array)

Quatro nomes de chave para a mesma conta, e um enum que aceita um valor por vez. **"Tudo
numa chamada" não existe nem em teoria.** Então:

    JUNTO      o lote congelado, o ID da conta, este arquivo, o normalizador, a porta
               paga (`coletor.executar`) e o dono da chave (`apify_pool`).
    SEPARADO   a execução, o teto de gasto, o manifesto, o artefato e — no caso do
               comentário — o tratamento jurídico.

E há um motivo que sobrevive mesmo se a Apify mudar o contrato amanhã: **as camadas
quebram de jeitos diferentes**. Bio quebra por perfil; post quebra por muro; reel quebra
por preço de transcrição; comentário quebra por teto de plano E por dado pessoal. Um
artefato único esconderia qual das quatro quebrou.

O QUE RODA ANTES DE PAGAR, E NÃO É CERIMÔNIA
----------------------------------------------
`contratos`, `plano` e `janela` custam ZERO e respondem, cada uma, uma pergunta que só se
responde caro depois:

    contratos  o ator aceita os campos que eu vou mandar? (8 execuções desta casa já
               foram queimadas mandando campo que o Actor descartava em silêncio)
    plano      em que faixa a chave está? O mesmo trabalho custa 5x mais no FREE que no
               DIAMOND, e há ator com teto de 5 URLs por run no plano gratuito.
    janela     o que a rota GRÁTIS já entrega? Medido: bio, seguidores, os 12 posts mais
               recentes, a legenda INTEIRA, a data exata, curtidas, e — em reel — as
               visualizações e a duração. Pagar por isso seria pagar duas vezes.

    O QUE A ROTA GRÁTIS NÃO DÁ, E É O ÚNICO MOTIVO REAL DE PAGAR:
      · o TEXTO dos comentários;
      · qualquer coisa além dos 12 itens mais recentes de cada conta.

PORTÃO ENTRE FASES
-------------------
Fase paga NÃO roda se a anterior tiver qualquer `PARTIAL`. O operador decide seguir —
não descobre depois. E `liquidar` roda depois de CADA fase paga, nunca só no fim: quem
autoriza a fase seguinte precisa ver a fatura da anterior, não a estimativa dela.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap          # noqa: E402  — dono único da rotação de chave
import coletor                   # noqa: E402  — porta única das rotas pagas
import contrato_ator as ca       # noqa: E402  — o portão grátis do gasto
import instagram_pessoal as ip   # noqa: E402  — dono único do dado pessoal

SAMPLES = os.path.join(ROOT, 'data', 'samples')
LOTE = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM', 'PUBLIC-COMM-FIRST-BATCH-EAME.json')
JANELA_DIR = os.path.join(SAMPLES, 'INSTAGRAM-JANELA')
SAIDA = os.path.join(SAMPLES, 'INSTAGRAM-COLETA')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

# A janela. 30 dias primeiro; 90 SÓ se o corpus vier baixo, com o número que motivou
# gravado. Sem a janela no item, um silêncio não sabe dizer se é da empresa ou da janela.
JANELA_DIAS = int(os.environ.get('IG_JANELA_DIAS') or 30)
JANELA_AMPLIADA = 90
CORPUS_BAIXO = 5                # itens por conta abaixo disto autorizam ampliar

# ── ATORES, COM O BUILD LIDO EM 2026-09-02 ──────────────────────────────────────
# O build vai FIXO na URL do POST (`&build=`). Os quatro atores oficiais foram
# reconstruídos no MESMO minuto de 2026-08-31: a cadência é semanal, e "entrada provada
# ontem" aqui tem prazo medido em DIAS. Fixar o build é o que torna a coleta repetível.
# Quando o build mudar, `contratos` levanta BUILD_DRIFT e a fase paga não roda.
ATORES = {
    'bio':         ('apify~instagram-profile-scraper', '0.0.601'),
    'posts':       ('apify~instagram-scraper', '0.0.776'),
    'reels':       ('apify~instagram-reel-scraper', '0.0.563'),
    'comentarios': ('scrapesmith~instagram-comments-scraper', '0.0.164'),
}

# Teto de gasto POR EXECUÇÃO, em dólar, aplicado pela própria Apify (`maxTotalChargeUsd`).
# É a única trava que funciona mesmo se este arquivo tiver um defeito de leitura de custo —
# e esta casa já anunciou US$0,90 e gastou US$5,04 por ler cedo demais.
TETO = {'bio': 0.05, 'posts': 0.20, 'reels': 0.10, 'comentarios': 0.15}


# ────────────────────────────────────────────────────────────────────── utilidades
def contas():
    if not os.path.exists(LOTE):
        raise SystemExit('sem lote congelado em %s' % LOTE)
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    return [c for c in d['ACCOUNTS'] if c.get('PLATFORM') == 'INSTAGRAM']


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/INSTAGRAM-COLETA/' + nome


def _ler(pasta, nome):
    p = os.path.join(pasta, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _desde(dias):
    import datetime
    return (datetime.date.today() - datetime.timedelta(days=dias)).isoformat()


def _entrada(fase, conta, dias):
    """A entrada de cada ator, com os NOMES DE CAMPO lidos do schema real do build.

    Quatro nomes diferentes para "a conta": `usernames`, `directUrls`, `username`,
    `postUrls`. Não é descuido dos autores dos atores — é o motivo pelo qual as camadas
    não podem ser uma chamada só.
    """
    handle, url = conta['ACCOUNT_HANDLE'], conta['ACCOUNT_URL']
    if fase == 'bio':
        # `includeAboutSection` fica FALSE: o add-on custa mais que o próprio perfil, e o
        # país da conta já foi provado de graça na fase de identidade. Pagar para
        # redecidir o que já está provado reabre decisão fechada.
        return {'usernames': [handle], 'includeAboutSection': False}
    if fase == 'posts':
        return {'directUrls': [url], 'resultsType': 'posts', 'resultsLimit': 50,
                'onlyPostsNewerThan': _desde(dias), 'addParentData': False}
    if fase == 'reels':
        # Os três add-ons ficam FALSE por constante, não por descuido:
        # `includeTranscript` custa por MINUTO INICIADO por reel — um reel de 61 s paga
        # 2 minutos, e o add-on chega a valer 18x o próprio reel. Ligar isso "só para
        # ver" é o erro mais caro que este arquivo pode cometer.
        # `skipPinnedPosts` fica FALSE de propósito: o post fixado costuma ser o
        # manifesto de campanha da marca, que é exatamente o que a missão procura.
        return {'username': [handle], 'resultsLimit': 25,
                'onlyPostsNewerThan': _desde(dias),
                'skipPinnedPosts': False, 'skipTrialReels': False,
                'includeSharesCount': False, 'includeTranscript': False,
                'includeDownloadedVideo': False}
    raise ValueError('fase sem contrato de entrada: %s' % fase)


def _entrada_comentarios(urls, por_post=20):
    # `sortOrder` vai EXPLÍCITO. O default publicado é "popular", que não pagina até a
    # completude e enviesa a amostra para o comentário mais curtido — e a DESCRIÇÃO do
    # campo chega a sugerir `recent_activity`, valor que o enum não aceita.
    return {'postUrls': list(urls), 'maxCommentsPerPost': int(por_post),
            'sortOrder': 'recent'}


# ══════════════════════════════════════════════════════ FASE GRÁTIS · CONTRATOS
def contratos():
    """GET no ator e no build. Zero run, zero custo, zero credencial necessária."""
    cs = contas()
    fora, todos_ok = [], True
    for fase, (ator, build) in sorted(ATORES.items()):
        entrada = (_entrada_comentarios(['https://www.instagram.com/p/EXEMPLO/'])
                   if fase == 'comentarios' else _entrada(fase, cs[0], JANELA_DIAS))
        r, ok = ca.portao(ator, entrada, build_esperado=build)
        r['FASE'] = fase
        r['BUILD_ESPERADO'] = build
        todos_ok = todos_ok and ok
        fora.append(r)
        print('%-12s %-42s build %-9s %s' % (fase, ator, r.get('BUILD_NUMBER'),
                                             'APROVADO' if ok else 'REPROVADO'))
        for p in r['PROBLEMS']:
            print('    [%s] %s — %s' % (p['GRAVIDADE'], p['CODIGO'], p['DETALHE'][:150]))
    caminho = _gravar('CONTRATOS.json', {
        'SOURCE_ID': 'INSTAGRAM-COLETA/CONTRATOS',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'GET /v2/acts/{ator} e /v2/actor-builds/{id} — leitura, zero execução',
        'SOURCE_LOCATION': 'Apify', 'FACT_LOCATION': 'n/a — descreve ferramenta',
        'CAPTURED_AT': coletor.agora(), 'MISSION': MISSION,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'ALL_APPROVED': 'YES' if todos_ok else 'NO',
        'REGRA': 'nenhuma fase paga roda com ALL_APPROVED = NO',
        'ACTORS': fora})
    print('\ngravado: %s · todos aprovados: %s' % (caminho, 'SIM' if todos_ok else 'NÃO'))
    return 0 if todos_ok else 1


# ══════════════════════════════════════════════════════════ FASE GRÁTIS · PLANO
def plano():
    """Em que faixa está cada chave. Muda o preço em até 5x — e há teto por plano.

    Sem isto, um lote de 25 URLs mandado a um ator com teto de 5 no plano gratuito volta
    com 5 itens e status `SUCCEEDED`. Cinco de vinte e cinco, apresentados como sucesso.
    """
    chaves = ap.pool()
    if not chaves:
        print('POOL_EMPTY — sem chave não dá para ler o plano. A leitura do CONTRATO, '
              'essa sim, roda sem chave: `py scripts/instagram_coleta.py contratos`.')
        return 1
    linhas = []
    for i, k in enumerate(chaves, 1):
        try:
            d = ca._get('%s/users/me' % coletor.API, token=k)
            u = (d or {}).get('data') or {}
            p = u.get('plan') or {}
            linhas.append({'POOL_POSITION': i,
                           'PLAN_ID': p.get('id') or NAO_SEI,
                           'PLAN_NAME': p.get('description') or NAO_SEI,
                           'MONTHLY_USAGE_USD': (p.get('monthlyUsageCreditsUsd')
                                                 if p else NAO_SEI),
                           'STATE': 'READ_OK'})
        except Exception as e:                                # noqa: BLE001
            linhas.append({'POOL_POSITION': i, 'STATE': 'NOT_READ',
                           'WHY': ap.redigir('%s: %s' % (type(e).__name__, e))[:160]})
        print('  posicao %d: %s' % (i, linhas[-1].get('PLAN_ID') or linhas[-1].get('WHY')))
    caminho = _gravar('PLANO-DAS-CHAVES.json', {
        'SOURCE_ID': 'INSTAGRAM-COLETA/PLANO-DAS-CHAVES',
        'source': 'GET /v2/users/me — leitura, zero execução',
        'CAPTURED_AT': coletor.agora(), 'APIFY_RUNS': 0, 'COST_USD': 0,
        'NUNCA_GRAVAR_TOKEN': 'só a POSIÇÃO no pool e o plano. Valor de chave, jamais.',
        'POR_QUE_IMPORTA': (
            'o mesmo trabalho custa até 5x mais no FREE que no DIAMOND, e há ator com '
            'teto de 5 URLs por execução no plano gratuito. Lote de 25 volta 5 e sai '
            'SUCCEEDED — cinco de vinte e cinco, apresentados como sucesso.'),
        'KEYS': linhas})
    print('\ngravado: %s' % caminho)
    return 0


# ══════════════════════════════════════════════════════════ FASE GRÁTIS · JANELA
def janela():
    """Delega para a rota do navegador. Aqui só para a ordem das fases ficar num lugar."""
    import instagram_janela as ij
    return ij.perfis() or ij.objetos()


# ═══════════════════════════════════════════════════════════════ FASES PAGAS
def _portao_da_fase_anterior(fase):
    """Fase paga não roda depois de PARTIAL. O operador decide seguir; não descobre."""
    ordem = ['bio', 'posts', 'reels', 'comentarios']
    if fase not in ordem or ordem.index(fase) == 0:
        return True, ''
    anterior = ordem[ordem.index(fase) - 1]
    art = _ler(SAIDA, '%s.json' % anterior.upper())
    if not art:
        return False, ('a fase `%s` ainda não rodou. A ordem existe porque a bio é o '
                       'teste de fumaça de 1 centavo: se ela vier vazia, a rota paga '
                       'está quebrada e você descobriu barato.' % anterior)
    if art.get('PARTIAL_RUNS'):
        return False, ('a fase `%s` teve %d execução(ões) PARTIAL. Seguir agora seria '
                       'empilhar coleta sobre retrato incompleto. Veja %s.json e decida '
                       'à mão — para forçar, IG_IGNORAR_PORTAO=1.'
                       % (anterior, art['PARTIAL_RUNS'], anterior.upper()))
    return True, ''


def _rodar(fase, entrada, *, run_id, conta, evidencia):
    """Uma execução paga, pela porta única, com teto e build fixos."""
    ator, build = ATORES[fase]
    chaves = ap.pool()
    if not chaves:
        return [], None, ap.POOL_EMPTY
    ultimo = ([], None)
    for pos, k in enumerate(chaves, 1):
        itens, man = coletor.executar(
            ator, entrada, token=k, run_id='%s-p%d' % (run_id, pos),
            platform='INSTAGRAM', country=(conta or {}).get('COUNTRY', 'MULTI'),
            mission=MISSION, query=(conta or {}).get('ACCOUNT_URL', run_id),
            source_version='build %s, captura de %s' % (build, coletor.agora()[:10]),
            evidence_path=evidencia, teto_usd=TETO[fase], build=build)
        man['TOKEN_POSITION_USED'] = pos
        man['RUNNER_NAME'] = RUNNER
        man['FASE'] = fase
        estado = ap.classificar(status=man.get('PLATFORM_STATUS'),
                                status_message=str(man.get('ERROR') or ''), itens=itens)
        ultimo = (itens, man)
        if itens:
            return itens, man, estado
        if estado in ap.ROTACIONAM:
            print('      posicao %d esgotada (%s) -> trocando' % (pos, estado))
            continue
        return itens, man, estado          # vazio legítimo: não gastar outra chave
    return ultimo[0], ultimo[1], 'POOL_EXHAUSTED'


def _fase_por_conta(fase, dias=None):
    """bio, posts e reels: um run POR CONTA, e isso é decisão medida.

    Numa batelada de 5 contas, um buraco de 85% numa delas se dilui e some. Separado, o
    buraco fica em cima do nome da empresa. Custa o mesmo (pay-per-result) e compra um
    diagnóstico de graça.
    """
    ok, motivo = _portao_da_fase_anterior(fase)
    if not ok and not os.environ.get('IG_IGNORAR_PORTAO'):
        print('PORTÃO FECHADO: %s' % motivo)
        return 1
    dias = dias or JANELA_DIAS
    cs = contas()
    ator, build = ATORES[fase]

    # O contrato PRIMEIRO, sempre. Custa zero e é o que impede as 8 execuções queimadas.
    r, aprovado = ca.portao(ator, _entrada(fase, cs[0], dias), build_esperado=build)
    if not aprovado:
        print('CONTRATO REPROVADO — nenhuma execução foi disparada, custo zero:')
        for p in r['PROBLEMS']:
            print('   [%s] %s — %s' % (p['GRAVIDADE'], p['CODIGO'], p['DETALHE'][:200]))
        _gravar('%s.json' % fase.upper(), {
            'SOURCE_ID': 'INSTAGRAM-COLETA/%s' % fase.upper(),
            'STATE': 'BLOCKED_BY_CONTRACT_GATE', 'CONTRACT': r,
            'APIFY_RUNS': 0, 'COST_USD': 0, 'ITEM_COUNT': 0,
            'ZERO_SIGNIFICA': ('nenhuma execução foi disparada. Isto NÃO é "as contas '
                               'não publicam" — é o portão de contrato tendo funcionado.'),
            'CAPTURED_AT': coletor.agora(), 'ITEMS': []})
        return 1

    print('%s · %d contas · janela %d dias · ator %s build %s · teto US$%.2f/run'
          % (fase, len(cs), dias, ator, build, TETO[fase]))
    itens_todos, mans, parciais = [], [], 0
    for c in cs:
        rid = 'IG-%s-%s-%s' % (fase.upper(), c['COMPANY'], c['COUNTRY'])
        itens, man, estado = _rodar(
            fase, _entrada(fase, c, dias), run_id=rid, conta=c,
            evidencia='data/samples/INSTAGRAM-COLETA/%s.json' % fase.upper())
        if man is None:
            print('  %-16s POOL_EMPTY — sem chave, nada foi gastado' % c['ACCOUNT_HANDLE'])
            continue
        mans.append(man)
        parciais += 1 if man['STATUS'] == 'PARTIAL' else 0
        for b in (itens or []):
            itens_todos.append(_normalizar(b, c, fase, dias, man))
        print('  %-16s %-8s itens=%-4d terminal=%-3s falhadas=%s'
              % (c['ACCOUNT_HANDLE'], man['STATUS'], len(itens or []),
                 man.get('RUN_REACHED_TERMINAL'), man.get('REQUESTS_FAILED')))

    return _gravar_fase(fase, cs, itens_todos, mans, parciais, dias)


def _gravar_fase(fase, cs, itens, mans, parciais, dias):
    caminho = _gravar('%s.json' % fase.upper(), {
        'SOURCE_ID': 'INSTAGRAM-COLETA/%s' % fase.upper(),
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'contas oficiais LOCAIS provadas, via Apify, um run por conta',
        'SOURCE_LOCATION': 'Instagram',
        'FACT_LOCATION': 'NOT_KNOWN — decidido item a item, depois, de graça',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'CAPTURED_AT': coletor.agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'ACTOR': ATORES[fase][0], 'BUILD_PINNED': ATORES[fase][1],
        'MAX_TOTAL_CHARGE_USD_PER_RUN': TETO[fase],
        'COLLECTION_WINDOW_DAYS': dias, 'COLLECTION_WINDOW_FROM': _desde(dias),
        'ACCOUNTS_ATTEMPTED': len(cs), 'APIFY_RUNS': len(mans),
        'PARTIAL_RUNS': parciais,
        'RUNS_NOT_TERMINAL': sum(1 for m in mans if m.get('RUN_REACHED_TERMINAL') == 'NO'),
        'ITEM_COUNT': len(itens),
        # O custo NUNCA é anunciado a partir do que o run devolveu na hora.
        'COST_USD': NAO_SEI,
        'COST_STATE': 'NOT_SETTLED',
        'COST_AT_WRITE_TIME': sum(m.get('COST_USD') or 0 for m in mans
                                  if isinstance(m.get('COST_USD'), (int, float))),
        'COST_WARNING': ('o valor acima é o que a plataforma devolveu ANTES de fechar a '
                         'conta, e vem 0. Rode `liquidar` — um piloto desta casa '
                         'anunciou US$0,90 e gastou US$5,04.'),
        'ZERO_SIGNIFICA': ('itens=0 com PARTIAL_RUNS>0 é falha de coleta, não silêncio '
                           'da empresa. SOURCE FAILURE != ZERO.'),
        'RUNS': mans, 'ITEMS': itens})
    print('\ngravado: %s · itens=%d · runs=%d · PARCIAIS=%d'
          % (caminho, len(itens), len(mans), parciais))
    print('  custo: NÃO LIQUIDADO — rode `py scripts/instagram_coleta.py liquidar`')
    return 0


def _normalizar(bruto, conta, fase, dias, man):
    """RAW → os campos da casa. O que a fonte não deu sai NOT_KNOWN, nunca vazio."""
    def g(*nomes):
        for n in nomes:
            v = bruto.get(n)
            if v not in (None, '', [], {}):
                return v
        return NAO_SEI

    return {
        'OBJECT_ID': g('id', 'shortCode', 'shortcode', 'postId', 'url'),
        'SHORTCODE': g('shortCode', 'shortcode', 'code'),
        'ACCOUNT_HANDLE': conta['ACCOUNT_HANDLE'],
        'ACCOUNT_URL': conta['ACCOUNT_URL'],
        'COMPANY': conta['COMPANY'],
        'COUNTRY_SCOPE': conta['COUNTRY'],
        'PLATFORM': 'INSTAGRAM',
        'LAYER': fase.upper(),
        'PUBLISHED_AT': g('timestamp', 'takenAt', 'date', 'publishedAt'),
        'URL': g('url', 'postUrl', 'link'),
        'CAPTION': g('caption', 'text', 'description'),
        'MEDIA_TYPE': g('type', 'productType', 'mediaType'),
        'LIKE_COUNT': g('likesCount', 'likeCount'),
        'COMMENT_COUNT': g('commentsCount', 'commentCount'),
        'VIDEO_VIEW_COUNT': g('videoViewCount', 'videoPlayCount', 'playCount'),
        'VIDEO_DURATION_S': g('videoDuration', 'duration'),
        'FOLLOWERS': g('followersCount', 'followers'),
        'BIO': g('biography', 'bio'),
        'COLLECTION_WINDOW_DAYS': dias,
        'COLLECTION_WINDOW_FROM': _desde(dias),
        # A cadeia de evidência fecha AQUI, no item — não só no manifesto. Sem isto todo
        # item nasce apontando para NOT_KNOWN e o RUN_ID volta a só agrupar registros.
        'COLLECTION_RUN_ID': man['RUN_ID'],
        'RAW_REFERENCE': man.get('RAW_EVIDENCE_PATH', NAO_SEI),
        'RAW_COMPLETENESS': man.get('RAW_COMPLETENESS', NAO_SEI),
        'ACTOR': man['ACTOR'], 'BUILD_PINNED': man.get('BUILD_PINNED', NAO_SEI),
        'DATASET_OWNER': DATASET_OWNER, 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'COUNTRY_OF_FACT': 'NOT_KNOWN', 'REGION_OF_FACT': 'NOT_KNOWN',
        # Medido: @bayer_italia é a conta guarda-chuva da empresa e publica saúde, não
        # agro. Sem esta marca, "a Bayer publicou X vezes" vira número falso.
        'SUBJECT_DOMAIN': 'NOT_CLASSIFIED',
    }


def bio():
    return _fase_por_conta('bio')


def posts():
    return _fase_por_conta('posts')


def reels():
    return _fase_por_conta('reels')


# ══════════════════════════════════════════════════ FASE PAGA · COMENTÁRIOS
def comentarios(por_post=20):
    """A única camada que a rota grátis não entrega — e a única com dado pessoal."""
    pode, motivo = ip.pode_coletar()
    if not pode:
        print('PORTÃO DE DADO PESSOAL FECHADO. Nada foi gasto.\n\n%s' % motivo)
        _gravar('COMENTARIOS.json', {
            'SOURCE_ID': 'INSTAGRAM-COLETA/COMENTARIOS',
            'STATE': 'BLOCKED_BY_PERSONAL_DATA_GATE', 'WHY': motivo,
            'APIFY_RUNS': 0, 'COST_USD': 0, 'ITEM_COUNT': 0,
            'ZERO_SIGNIFICA': ('o portão estava fechado. NÃO é "não há comentários" — '
                               'a rota grátis já mediu que há.'),
            'CAPTURED_AT': coletor.agora(), 'ITEMS': []})
        return 1
    ok, m = _portao_da_fase_anterior('comentarios')
    if not ok and not os.environ.get('IG_IGNORAR_PORTAO'):
        print('PORTÃO FECHADO: %s' % m)
        return 1

    # Os alvos saem da rota GRÁTIS: só objeto que já declarou comentário > 0. Pedir
    # comentário de post com zero comentário é gastar para receber vazio.
    objs = _ler(JANELA_DIR, 'OBJETOS.json')
    if not objs:
        print('sem OBJETOS.json — rode `janela` antes. Ela é grátis e diz onde há o quê.')
        return 1
    alvos = []
    for o in objs['ITEMS']:
        n = max([v for v in (o.get('COMMENT_COUNT_BY_ROUTE') or {}).values()
                 if isinstance(v, int)] or [0])
        if n > 0:
            alvos.append((o, n))
    alvos.sort(key=lambda t: -t[1])
    print('objetos com comentário declarado: %d de %d' % (len(alvos), len(objs['ITEMS'])))
    if not alvos:
        print('NADA A PEDIR — nenhum objeto declara comentário. Custo zero.')
        return 0

    ator, build = ATORES['comentarios']
    urls = ['https://www.instagram.com/p/%s/' % o['SHORTCODE'] for o, _ in alvos]
    ip.preparar_pasta()
    itens, mans, parciais = [], [], 0
    # Blocos pequenos: há ator com teto por run no plano gratuito, e bloco grande que
    # volta cortado sai `SUCCEEDED`. Bloco pequeno faz o corte aparecer.
    for i in range(0, len(urls), 10):
        pedaco = urls[i:i + 10]
        r, aprovado = ca.portao(ator, _entrada_comentarios(pedaco, por_post),
                                build_esperado=build)
        if not aprovado:
            print('CONTRATO REPROVADO no bloco %d — nada gasto' % (i // 10))
            for p in r['PROBLEMS']:
                print('   [%s] %s' % (p['GRAVIDADE'], p['CODIGO']))
            return 1
        brutos, man, _e = _rodar(
            'comentarios', _entrada_comentarios(pedaco, por_post),
            run_id='IG-COMENTARIOS-%d' % (i // 10), conta=None,
            evidencia='data/samples/INSTAGRAM-COLETA/COMENTARIOS.json')
        if man is None:
            print('  bloco %d: POOL_EMPTY' % (i // 10))
            continue
        mans.append(man)
        parciais += 1 if man['STATUS'] == 'PARTIAL' else 0
        por_sc = {o['SHORTCODE']: o for o, _ in alvos}
        for b in (brutos or []):
            sc = str(b.get('postUrl') or b.get('url') or '').rstrip('/').split('/')[-1]
            itens.append(ip.normalizar_comentario(
                b, objeto=por_sc.get(sc, {}), run_id=man['RUN_ID']))
        print('  bloco %d: %d comentários (%s)' % (i // 10, len(brutos or []), man['STATUS']))

    # Teto do plano gratuito disfarçado de audiência: dois ou mais posts voltando com
    # EXATAMENTE o mesmo número redondo é sinal de corte, não de engajamento.
    from collections import Counter
    por_obj = Counter(c['OBJECT_ID'] for c in itens)
    no_teto = [k for k, v in por_obj.items() if v == por_post]
    caminho = _gravar('COMENTARIOS.json', {
        'SOURCE_ID': 'INSTAGRAM-COLETA/COMENTARIOS',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'comentários públicos de posts das contas do lote, via Apify',
        'SOURCE_LOCATION': 'Instagram', 'FACT_LOCATION': 'NOT_KNOWN',
        'EVIDENCE_CLASS': 'FIELD_VOICE_OBSERVED',
        'CAPTURED_AT': coletor.agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'ACTOR': ator, 'BUILD_PINNED': build,
        'SORT_ORDER': 'recent — explícito. O default publicado é "popular", que enviesa.',
        'MAX_COMMENTS_PER_POST': por_post,
        'OBJECTS_ASKED': len(urls), 'APIFY_RUNS': len(mans), 'PARTIAL_RUNS': parciais,
        'ITEM_COUNT': len(itens),
        'CEILING_SUSPECTED': no_teto,
        'CEILING_WARNING': ('%d objeto(s) voltaram com EXATAMENTE %d comentários. Isto '
                            'pode ser o teto do pedido ou do plano, não a audiência.'
                            % (len(no_teto), por_post)) if no_teto else 'nenhum',
        'COST_USD': NAO_SEI, 'COST_STATE': 'NOT_SETTLED',
        'PERSONAL_DATA': 'YES',
        'LEGAL_REVIEW': 'PENDING',
        'RETENTION_STATE': ip.RETENCAO,
        'AUTHOR_HANDLES_STORED': 'NO — pseudônimo HMAC, sal fora do repositório',
        'PURGE_HOW': 'py scripts/instagram_pessoal.py expurgar --confirmar',
        'LEI': ('comentário é FIELD_VOICE_OBSERVED, nunca FIELD_PROBLEM_CONFIRMED. '
                'Voz não é incidência.'),
        'ITEMS': itens})
    print('\ngravado: %s · comentários=%d · runs=%d' % (caminho, len(itens), len(mans)))
    return 0


# ══════════════════════════════════════════════════════ FASE GRÁTIS · LIQUIDAR
def liquidar():
    """O custo REAL, lido depois. GET não é execução: funciona com a chave esgotada."""
    chaves = ap.pool()
    if not chaves:
        print('POOL_EMPTY — sem chave não dá para ler a fatura.')
        return 1
    import corrigir_custo as cc
    reais = {}
    for k in chaves:
        try:
            reais.update(cc._runs_reais(k))
        except Exception as e:                                # noqa: BLE001
            print('  chave não leu:', ap.redigir(str(e))[:100])
    total, tocados = 0.0, []
    for nome in ('BIO.json', 'POSTS.json', 'REELS.json', 'COMENTARIOS.json'):
        art = _ler(SAIDA, nome)
        if not art:
            continue
        soma = 0.0
        for m in art.get('RUNS') or []:
            par = reais.get(m.get('DATASET_ID'))
            usd = (par[0] if isinstance(par, tuple) else par) if par else None
            if usd is None:
                m['COST_STATE'] = 'NOT_FOUND_IN_PLATFORM_LIST'
                continue
            m['COST_USD_AT_WRITE_TIME'] = m.get('COST_USD')
            m['COST_USD'] = usd
            m['COST_STATE'] = 'SETTLED'
            soma += float(usd)
        art['COST_USD'] = round(soma, 6)
        art['COST_STATE'] = 'SETTLED'
        art['COST_SETTLED_AT'] = coletor.agora()
        _gravar(nome, art)
        total += soma
        tocados.append('%s = US$ %.4f' % (nome, soma))
        print('  %-20s US$ %.4f' % (nome, soma))
    print('\nCUSTO REAL TOTAL: US$ %.4f' % total)
    _gravar('CUSTO-LIQUIDADO.json', {
        'SOURCE_ID': 'INSTAGRAM-COLETA/CUSTO-LIQUIDADO',
        'source': 'GET /v2/actor-runs casado por DATASET_ID — leitura, não execução',
        'CAPTURED_AT': coletor.agora(), 'TOTAL_USD': round(total, 6),
        'BY_ARTIFACT': tocados,
        'LEI': 'CUSTO LIDO CEDO DEMAIS NÃO É CUSTO ZERO.'})
    return 0


# ══════════════════════════════════════════════════════ FASE GRÁTIS · SEMÁFORO
def semaforo():
    """A grade: 5 contas × as camadas. Cada célula é um ESTADO, não uma contagem."""
    cs = contas()
    perfis = _ler(JANELA_DIR, 'PERFIS.json') or {'ITEMS': []}
    objs = _ler(JANELA_DIR, 'OBJETOS.json') or {'ITEMS': []}
    por_conta_perfil = {p['ACCOUNT_HANDLE']: p for p in perfis['ITEMS']}
    grade, alertas = [], []
    for c in cs:
        h = c['ACCOUNT_HANDLE']
        p = por_conta_perfil.get(h) or {}
        meus = [o for o in objs['ITEMS'] if o.get('ACCOUNT_HANDLE') == h]
        denom = p.get('ACCOUNT_POST_COUNT')
        linha = {
            'ACCOUNT_HANDLE': h, 'COMPANY': c['COMPANY'], 'COUNTRY_SCOPE': c['COUNTRY'],
            'BIO_GRATIS': 'PRESENTE' if p.get('BIO_TEXT') not in (None, NAO_SEI) else 'AUSENTE',
            'PORTA': p.get('DOOR_STATE', NAO_SEI),
            'GRADE_VISIVEL': p.get('GRID_ITEMS_VISIBLE', NAO_SEI),
            'POSTS_DA_CONTA': denom if denom else NAO_SEI,
            'OBJETOS_LIDOS': len(meus),
            'COM_DATA': sum(1 for o in meus if o.get('PUBLISHED_AT') not in (None, NAO_SEI)),
            'COM_LEGENDA': sum(1 for o in meus if o.get('CAPTION') not in (None, NAO_SEI)),
            'VIDEOS': sum(1 for o in meus if o.get('IS_VIDEO') == 'YES'),
            'TEXTO_DE_COMENTARIO': 'AUSENTE — nenhuma rota grátis entrega',
        }
        for fase in ('BIO', 'POSTS', 'REELS', 'COMENTARIOS'):
            art = _ler(SAIDA, '%s.json' % fase)
            if not art:
                linha['PAGO_%s' % fase] = 'NAO_RODOU'
            elif art.get('STATE', '').startswith('BLOCKED'):
                linha['PAGO_%s' % fase] = art['STATE']
            else:
                n = len([i for i in art.get('ITEMS') or []
                         if i.get('ACCOUNT_HANDLE') == h])
                linha['PAGO_%s' % fase] = ('PARCIAL(%d)' % n if art.get('PARTIAL_RUNS')
                                           else 'PRESENTE(%d)' % n if n else 'ZERO')
        # A contradição que a contagem sozinha nunca acusa.
        if linha['BIO_GRATIS'] == 'PRESENTE' and linha['OBJETOS_LIDOS'] == 0:
            alertas.append('%s: a bio leu mas nenhum objeto leu. Isto NÃO é conta vazia '
                           '— é rota parcial.' % h)
        if isinstance(denom, int) and linha['OBJETOS_LIDOS'] < denom:
            alertas.append('%s: %d de %d posts — SUB-COLETA DECLARADA (teto da rota).'
                           % (h, linha['OBJETOS_LIDOS'], denom))
        grade.append(linha)

    caminho = _gravar('SEMAFORO.json', {
        'SOURCE_ID': 'INSTAGRAM-COLETA/SEMAFORO',
        'source': 'grade derivada dos artefatos — nenhum número é digitado',
        'CAPTURED_AT': coletor.agora(), 'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_A_CONTAGEM_NAO_DIZ': (
            'itens=0 pode ser: rota bloqueada, portão fechado, janela sem publicação, ou '
            'coleta quebrada. Cada célula carrega o ESTADO, não só o número.'),
        'ALERTAS': alertas, 'GRADE': grade})
    largura = max(len(l['ACCOUNT_HANDLE']) for l in grade) if grade else 10
    print('%-*s %-8s %-7s %-9s %-8s %-8s %s' % (largura, 'conta', 'porta', 'grade',
                                                'do total', 'c/ data', 'videos', 'pago'))
    for l in grade:
        print('%-*s %-8s %-7s %-9s %-8s %-8s %s'
              % (largura, l['ACCOUNT_HANDLE'], str(l['PORTA'])[:8],
                 l['GRADE_VISIVEL'], l['POSTS_DA_CONTA'], l['COM_DATA'], l['VIDEOS'],
                 l.get('PAGO_POSTS')))
    if alertas:
        print('\nALERTAS:')
        for a in alertas:
            print('  ·', a)
    print('\ngravado: %s' % caminho)
    return 0


FASES = {'contratos': contratos, 'plano': plano, 'janela': janela,
         'bio': bio, 'posts': posts, 'reels': reels,
         'comentarios': comentarios, 'liquidar': liquidar, 'semaforo': semaforo}

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'contratos'
    if cmd not in FASES:
        print('uso: instagram_coleta.py {%s}' % '|'.join(FASES))
        raise SystemExit(2)
    raise SystemExit(FASES[cmd]())
