#!/usr/bin/env python3
"""
COLETA DO ACERVO — o material público dos 10 canais congelados.

    py scripts/creator_corpus_coleta.py contratos     # GRÁTIS — lê o schema dos atores
    py scripts/creator_corpus_coleta.py instagram     # posts dos canais Instagram
    py scripts/creator_corpus_coleta.py youtube       # vídeos do canal YouTube
    py scripts/creator_corpus_coleta.py comentarios   # amostra de comentários

SOURCE-FIRST, TOOL-SECOND
---------------------------
O Apify é a rota, não a fonte. A fonte é o canal público que o Creator Map já
provou. Por isso a coleta parte SEMPRE do `PUBLIC_CHANNEL` do universo fechado,
nunca de uma busca por nome nem do campo `HANDLE`: `NAME_MATCH != PERSON` já
custou a esta casa o presidente da Unione Petrolifera promovido a pesquisador
de trigo duro, e o `HANDLE` do artefato congelado carrega o nome de exibição
junto em pelo menos um caso (`@chaineagricole (Chaine Agricole)`) — que, enviado
a um ator, viraria perfil inexistente, e perfil inexistente devolve zero itens,
que se lê como "a pessoa não publica".

POR QUE A FASE `contratos` VEM ANTES DE QUALQUER GASTO
--------------------------------------------------------
Ator descarta em SILÊNCIO o campo de entrada que não reconhece. Medido nesta
casa: oito execuções pagas devolveram oito vezes o mesmo consultor de
cibersegurança porque o campo enviado não existia no schema. Ler o schema é
grátis. Descobrir com dinheiro que ele era outro, não.

ISOLAMENTO ENTRE MISSÕES
--------------------------
`RUN_MANIFEST` e `raw-paid` próprios, no diretório desta missão. O Creator Map
já mediu o preço de dois runners gravando o mesmo JSON: `pv.gravar()` lê tudo,
junta e reescreve o arquivo inteiro — quem termina por último apaga o outro. A
correção não é lock, é NAMESPACE.

O QUE ESTA FASE NÃO FAZ
-------------------------
Não resolve identidade (é do Creator Map, e está congelada). Não abre creator
novo. Não decide relevância — isso é a fase de análise, e depende de material
que ainda não existe quando esta roda.
"""
import contextlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap                                      # noqa: E402
import coletor                                               # noqa: E402
import creator_corpus as cc                                  # noqa: E402
import proveniencia as pv                                    # noqa: E402

# A mesma substituição que o Creator Map fez, e pelo mesmo motivo medido:
# `coletor._curl` chama `curl` por subprocess e no runner Windows devolveu
# stdout VAZIO de forma intermitente — `json.loads(None)` virava um `TypeError`
# que não diz nada sobre a causa. Sem processo filho, sem pipe, sem shell.
# A troca é por SUBSTITUIÇÃO, não por desvio: toda a proveniência continua
# passando pela porta única do `coletor`.
from creator_coleta import _http                             # noqa: E402

MANIFESTO_DA_MISSAO = os.path.join(cc.BASE, 'RUN-MANIFEST-CORPUS.json')
RAW_DIR_DA_MISSAO = os.path.join(cc.BASE, 'raw-paid')


# O mesmo escopo do Creator Map, e pelo mesmo motivo medido: aplicar a troca no
# corpo do modulo fazia com que importar este ficheiro mudasse o manifesto da
# casa para o resto do processo. E este era o pior dos dois, porque
# `from creator_coleta import _http` ja executava o outro modulo antes, e o
# vencedor era simplesmente o ultimo a ser importado.
def _reconciliar_barrada(*_a, **_k):
    raise RuntimeError(
        'pv.reconciliar() dentro de escopo_da_missao() escreveria os fragmentos de '
        'TODOS os donos dentro do manifesto desta missao. Reconcilie fora do escopo.')


@contextlib.contextmanager
def escopo_da_missao():
    """Aponta coletor e proveniencia para o namespace desta missao, e devolve."""
    antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl, pv.reconciliar)
    pv.MANIFESTO = MANIFESTO_DA_MISSAO
    coletor.RAW_DIR = RAW_DIR_DA_MISSAO
    coletor._curl = _http
    # `pv.reconciliar()` deriva o indice a partir de TODOS os fragmentos da casa e
    # grava-o em `pv.MANIFESTO`. Com o manifesto redirecionado, isso despejaria os
    # donos todos dentro do namespace desta missao — em silencio, que e a pior
    # maneira. Nenhum sitio destes scripts chama `registrar(..., reconciliar=True)`
    # hoje, entao isto nao muda comportamento nenhum: transforma um defeito latente
    # num erro que se le. A reconciliacao continua permitida FORA do escopo, que e
    # onde ela faz sentido.
    pv.reconciliar = _reconciliar_barrada
    try:
        yield
    finally:
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl, pv.reconciliar = antes

MISSION = cc.MISSION

# Atores. Os de perfil já foram provados pelo Creator Map; os de POST e de
# COMENTÁRIO são novos nesta casa, e é por eles que a fase `contratos` existe.
ATORES = {
    'INSTAGRAM_POSTS':    'apify~instagram-scraper',
    'INSTAGRAM_COMMENTS': 'apify~instagram-comment-scraper',
    'YOUTUBE':            'streamers~youtube-scraper',
    'TIKTOK':             'clockworks~tiktok-scraper',
}

# Os campos que as fases pagas pretendem enviar. Declarados aqui para que a fase
# GRÁTIS possa conferi-los contra o schema antes de qualquer gasto.
ENTRADA_PRETENDIDA = {
    'INSTAGRAM_POSTS': ['directUrls', 'resultsType', 'resultsLimit', 'addParentData'],
    'INSTAGRAM_COMMENTS': ['directUrls', 'resultsLimit'],
    'YOUTUBE': ['startUrls', 'maxResults', 'sortVideosBy', 'downloadSubtitles',
                'preferAutoGeneratedSubtitles', 'subtitlesFormat', 'saveSubsToKVS'],
    'TIKTOK': [],
}

# §3 · alvo de PROFUNDIDADE, não régua. Se o canal não tiver 30, registra-se o
# N real — corpus não se inventa para bater alvo.
ALVO_POR_CANAL = 50
ALVO_MINIMO_DESEJADO = 30
# §10 · amostra de comentários só dos materiais mais relevantes.
MATERIAIS_COM_COMENTARIO = 8
COMENTARIOS_POR_MATERIAL = 30


def _pool():
    chaves = ap.pool()
    if not chaves:
        print('POOL_EMPTY — APIFY_TOKEN_POOL ausente ou vazia'); raise SystemExit(1)
    return chaves


def _entidades(plataforma=None):
    universo = cc.carregar('CORPUS-UNIVERSE.json')
    if not universo:
        print('UNIVERSO_AUSENTE — rode antes: py scripts/creator_corpus.py universo')
        raise SystemExit(1)
    alvo = [e for e in universo if e['COLLECTABLE'] == 'YES']
    if plataforma:
        alvo = [e for e in alvo if e['PLATFORM'] == plataforma]
    return alvo


# ═══════════════════════════════════════════════════ fase GRÁTIS
def contratos():
    """Lê ator E schema de entrada. Zero run, zero item, zero custo.

    Duas chamadas, e não uma. `AVAILABLE` prova que o ator existe — não que a
    entrada que vamos mandar é a que ele aceita. O INPUT SCHEMA não vem no
    objeto do ator: ele vive na BUILD, e só a segunda chamada o traz. A primeira
    versão desta fase leu `inputSchema` dentro de `taggedBuilds.latest` e
    devolveu `campos=0` para os quatro atores — um contrato vazio que se
    apresentava como contrato lido, que é exatamente o defeito que esta fase
    existe para não ter.
    """
    chaves = _pool()
    fora = []
    for rotulo, actor in ATORES.items():
        registro = {'LABEL': rotulo, 'ACTOR': actor}
        try:
            d = _http('https://api.apify.com/v2/acts/%s' % actor,
                      token=chaves[0], timeout=60).get('data') or {}
            registro.update(STATE='AVAILABLE', TITLE=d.get('title'),
                            USERNAME=d.get('username'))
            bid = ((d.get('taggedBuilds') or {}).get('latest') or {}).get('buildId')
            campos, obrigatorios = cc.NOT_KNOWN, cc.NOT_KNOWN
            if bid:
                b = (_http('https://api.apify.com/v2/actor-builds/%s' % bid,
                           token=chaves[0], timeout=60).get('data') or {})
                bruto = b.get('inputSchema')
                if isinstance(bruto, str):
                    bruto = json.loads(bruto or '{}')
                bruto = bruto or {}
                campos = sorted(bruto.get('properties') or {})
                obrigatorios = bruto.get('required') or []
            registro['INPUT_FIELDS'] = campos
            registro['REQUIRED'] = obrigatorios
            # O contrato só está LIDO quando os campos vieram. Sem isso o estado
            # é outro, e precisa de nome próprio — senão uma leitura falha passa
            # por leitura boa.
            registro['CONTRACT_STATE'] = ('SCHEMA_READ' if isinstance(campos, list) and campos
                                          else 'SCHEMA_NOT_READ')
        except Exception as e:                               # noqa: BLE001
            registro.update(STATE='UNREACHABLE', CONTRACT_STATE='SCHEMA_NOT_READ',
                            ERROR=ap.redigir('%s: %s' % (type(e).__name__, str(e)[:160])))
        fora.append(registro)
        print('%-20s %-34s %-11s %s' % (rotulo, actor, registro['STATE'],
                                        registro.get('CONTRACT_STATE')))
        if isinstance(registro.get('INPUT_FIELDS'), list):
            print('   campos:', ', '.join(registro['INPUT_FIELDS']))
            print('   obrigatórios:', registro.get('REQUIRED'))
    # A entrada que ESTA missão pretende mandar, conferida contra o schema lido.
    # É aqui que "o ator descarta em silêncio o campo que não reconhece" deixa
    # de ser uma lição e vira uma verificação.
    for registro in fora:
        pretendidos = ENTRADA_PRETENDIDA.get(registro['LABEL'], [])
        aceitos = registro.get('INPUT_FIELDS')
        if not isinstance(aceitos, list) or not aceitos:
            registro['FIELDS_WE_SEND_CHECK'] = 'NOT_CHECKED_SCHEMA_NOT_READ'
            continue
        rejeitados = [c for c in pretendidos if c not in aceitos]
        registro['FIELDS_WE_SEND'] = pretendidos
        registro['FIELDS_WE_SEND_REJECTED'] = rejeitados
        registro['FIELDS_WE_SEND_CHECK'] = 'OK' if not rejeitados else 'FIELD_NOT_IN_SCHEMA'
        if rejeitados:
            print('ATENÇÃO %s · campo fora do schema (seria descartado em '
                  'silêncio): %s' % (registro['LABEL'], ', '.join(rejeitados)))
    cc.gravar('ACTOR-CONTRACTS-CORPUS.json', {
        'CAPTURED_AT': coletor.agora(),
        'METHOD': 'GET /v2/acts/{actor} — leitura, zero run, zero custo',
        'WHY': 'ator descarta em silêncio o campo que não reconhece; ler o schema '
               'é grátis, descobrir com dinheiro que ele era outro não é.',
        'ACTORS': fora})


# ═══════════════════════════════════════════════════ Instagram
def instagram():
    """Posts públicos dos canais Instagram do universo fechado.

    Uma execução POR CANAL, e não uma execução com nove URLs. Custa mais
    chamadas e devolve algo que a chamada única não devolve: quando um canal
    falha, sabe-se QUAL falhou. Numa execução conjunta, nove canais e 200 itens
    não dizem se o décimo canal deu zero ou se o ator parou no meio — e "zero
    itens" lido como "não publica" é a leitura errada que esta casa já pagou.
    """
    chaves = _pool()
    alvo = _entidades('INSTAGRAM')
    print('CANAIS_INSTAGRAM=%d' % len(alvo))
    materiais, resumo = [], []
    for i, e in enumerate(alvo):
        chave = chaves[i % len(chaves)]
        url = e['PUBLIC_CHANNEL']
        run_id = '%s-IG-%s' % (MISSION, e['ENTITY_ID'])
        itens, man = coletor.executar(
            ATORES['INSTAGRAM_POSTS'],
            {'directUrls': [url], 'resultsType': 'posts',
             'resultsLimit': ALVO_POR_CANAL, 'addParentData': False},
            token=chave, run_id=run_id, platform='INSTAGRAM',
            country=e['COUNTRY'], mission=MISSION,
            query='acervo de %s (alvo %d)' % (e['HANDLE'], ALVO_POR_CANAL),
            source_version=cc.NAO_SEI,
            evidence_path='data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-MATERIALS.json')
        novos = [_material_ig(x, e, run_id) for x in itens]
        coletor.registrar(man, item_count_normalized=len(novos))
        materiais.extend(novos)
        resumo.append(_resumo_canal(e, novos, man))
        print('  %-6s %-24s %-8s itens=%-4d custo=%s' % (
            e['ENTITY_ID'], e['HANDLE'][:24], man['STATUS'], len(novos),
            man['COST_USD']))
    _persistir(materiais, resumo, 'INSTAGRAM')


def _material_ig(x, e, run_id):
    ts = (x.get('timestamp') or '')[:10]
    dias = _dias(ts)
    legenda = x.get('caption') or ''
    return cc.registro_vazio(
        CONTENT_ID='%s-IG-%s' % (e['ENTITY_ID'], x.get('shortCode') or x.get('id') or ''),
        PERSON_ID=e['PERSON_ID'], ENTITY_ID=e['ENTITY_ID'],
        PLATFORM='INSTAGRAM', URL=x.get('url') or cc.NOT_KNOWN,
        PUBLISHED_AT=ts or cc.NOT_KNOWN,
        FIRST_OBSERVED=coletor.agora()[:10], LAST_OBSERVED=coletor.agora()[:10],
        TEXT=legenda, CAPTION=legenda,
        TITLE=(legenda.split('\n')[0][:120] if legenda else cc.NOT_KNOWN),
        MEDIA_TYPE=x.get('type') or cc.NOT_KNOWN,
        PUBLIC_METRICS={'LIKES': x.get('likesCount'),
                        'COMMENTS': x.get('commentsCount'),
                        'VIDEO_VIEWS': x.get('videoViewCount')},
        RAW_REFERENCE=run_id, AS_OF_DATE=coletor.agora()[:10],
        RECENCY_WINDOW=cc.janela(dias),
        # Legenda vazia não é texto ausente: é uma publicação sem legenda. Os dois
        # casos parecem iguais no artefato se ninguém os separar aqui.
        TEXT_COMPLETENESS=('FULL_CAPTION' if legenda else 'NO_CAPTION_PUBLISHED'))


# ═══════════════════════════════════════════════════ YouTube
def youtube():
    """Vídeos públicos dos canais YouTube, com legenda quando o canal publicar.

    A legenda é o que transforma vídeo em TEXTO analisável. Sem ela, o material
    entra com título apenas — e `TEXT_COMPLETENESS` diz isso, para que nenhuma
    contagem de tema trate um título de cinco palavras como um vídeo lido.
    """
    chaves = _pool()
    alvo = _entidades('YOUTUBE')
    print('CANAIS_YOUTUBE=%d' % len(alvo))
    if not alvo:
        print('NADA_A_COLETAR=YES'); return
    materiais, resumo = [], []
    for i, e in enumerate(alvo):
        run_id = '%s-YT-%s' % (MISSION, e['ENTITY_ID'])
        itens, man = coletor.executar(
            ATORES['YOUTUBE'],
            {'startUrls': [{'url': e['PUBLIC_CHANNEL'].rstrip('/') + '/videos'}],
             'maxResults': ALVO_POR_CANAL, 'sortVideosBy': 'NEWEST',
             'downloadSubtitles': True, 'preferAutoGeneratedSubtitles': True,
             'subtitlesFormat': 'plaintext', 'saveSubsToKVS': False},
            token=chaves[i % len(chaves)], run_id=run_id, platform='YOUTUBE',
            country=e['COUNTRY'], mission=MISSION,
            query='acervo de %s (alvo %d)' % (e['HANDLE'], ALVO_POR_CANAL),
            source_version=cc.NAO_SEI,
            evidence_path='data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-MATERIALS.json')
        novos = [_material_yt(x, e, run_id) for x in itens]
        coletor.registrar(man, item_count_normalized=len(novos))
        materiais.extend(novos)
        resumo.append(_resumo_canal(e, novos, man))
        print('  %-6s %-24s %-8s itens=%-4d custo=%s' % (
            e['ENTITY_ID'], e['HANDLE'][:24], man['STATUS'], len(novos),
            man['COST_USD']))
    _persistir(materiais, resumo, 'YOUTUBE')


def _material_yt(x, e, run_id):
    data = (x.get('date') or x.get('uploadDate') or '')[:10]
    legendas = x.get('subtitles') or []
    texto = ''
    if isinstance(legendas, list) and legendas:
        primeira = legendas[0]
        texto = (primeira.get('plaintext') or primeira.get('srt') or ''
                 if isinstance(primeira, dict) else str(primeira))
    descricao = x.get('text') or x.get('description') or ''
    completo = ('FULL_TRANSCRIPT' if texto else
                'DESCRIPTION_ONLY' if descricao else 'TITLE_ONLY')
    return cc.registro_vazio(
        CONTENT_ID='%s-YT-%s' % (e['ENTITY_ID'], x.get('id') or ''),
        PERSON_ID=e['PERSON_ID'], ENTITY_ID=e['ENTITY_ID'],
        PLATFORM='YOUTUBE', URL=x.get('url') or cc.NOT_KNOWN,
        PUBLISHED_AT=data or cc.NOT_KNOWN,
        FIRST_OBSERVED=coletor.agora()[:10], LAST_OBSERVED=coletor.agora()[:10],
        TEXT=('%s\n%s' % (descricao, texto)).strip(), CAPTION=descricao,
        TITLE=x.get('title') or cc.NOT_KNOWN, MEDIA_TYPE='VIDEO',
        PUBLIC_METRICS={'VIEWS': x.get('viewCount'), 'LIKES': x.get('likes'),
                        'COMMENTS': x.get('commentsCount'),
                        'DURATION': x.get('duration')},
        RAW_REFERENCE=run_id, AS_OF_DATE=coletor.agora()[:10],
        RECENCY_WINDOW=cc.janela(_dias(data)),
        TEXT_COMPLETENESS=completo)


# ═══════════════════════════════════════════════════ comentários
def comentarios():
    """§10 · amostra de comentários dos materiais MAIS RELEVANTES de cada canal.

    Não é censo. Coletar todo comentário de todo material custaria muito e
    responderia menos: a pergunta é que TIPO de pergunta a audiência faz, e isso
    aparece na amostra. A seleção é por relevância técnica medida no texto, não
    por engajamento — ordenar por likes traria o material mais popular, que é
    outra pergunta.
    """
    chaves = _pool()
    materiais = cc.carregar('CORPUS-MATERIALS.json')
    if not materiais:
        print('SEM_MATERIAL — rode antes as fases instagram/youtube'); return
    porentidade = {}
    for m in materiais:
        porentidade.setdefault(m['ENTITY_ID'], []).append(m)

    fora, resumo = [], []
    for i, (eid, itens) in enumerate(sorted(porentidade.items())):
        ig = [m for m in itens if m['PLATFORM'] == 'INSTAGRAM'
              and m['URL'] != cc.NOT_KNOWN]
        escolhidos = sorted(ig, key=_peso_tecnico, reverse=True)[:MATERIAIS_COM_COMENTARIO]
        escolhidos = [m for m in escolhidos if _peso_tecnico(m) > 0] or escolhidos[:3]
        if not escolhidos:
            continue
        run_id = '%s-CM-%s' % (MISSION, eid)
        brutos, man = coletor.executar(
            ATORES['INSTAGRAM_COMMENTS'],
            {'directUrls': [m['URL'] for m in escolhidos],
             'resultsLimit': COMENTARIOS_POR_MATERIAL},
            token=chaves[i % len(chaves)], run_id=run_id, platform='INSTAGRAM',
            country=cc.NOT_KNOWN, mission=MISSION,
            query='amostra de comentários de %d materiais de %s' % (len(escolhidos), eid),
            source_version=cc.NAO_SEI,
            evidence_path='data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-COMMENTS.json')
        porurl = {m['URL'].rstrip('/'): m for m in escolhidos}
        for c in brutos:
            texto = c.get('text') or ''
            alvo = porurl.get((c.get('postUrl') or '').rstrip('/'))
            fora.append({
                'COMMENT_ID': c.get('id') or cc.NOT_KNOWN,
                'CONTENT_ID': alvo['CONTENT_ID'] if alvo else cc.NOT_KNOWN,
                'ENTITY_ID': eid,
                'PLATFORM': 'INSTAGRAM',
                'TEXT': texto,
                'PUBLISHED_AT': (c.get('timestamp') or '')[:10] or cc.NOT_KNOWN,
                'CLASS': cc.classificar_comentario(texto),
                'PUBLIC_METRICS': {'LIKES': c.get('likesCount')},
                'RAW_REFERENCE': run_id,
                'AS_OF_DATE': coletor.agora()[:10],
                'COMMENTER_ROLE': 'NOT_KNOWN',
                'LAW': cc.COMENTARISTA_NAO_E,
            })
        coletor.registrar(man, item_count_normalized=len(brutos))
        resumo.append({'ENTITY_ID': eid, 'MATERIALS_SAMPLED': len(escolhidos),
                       'COMMENTS_COLLECTED': len(brutos), 'RUN_STATUS': man['STATUS'],
                       'COST_USD': man['COST_USD']})
        print('  %-6s materiais=%-3d comentários=%-4d %s' % (
            eid, len(escolhidos), len(brutos), man['STATUS']))

    from collections import Counter
    anterior = cc.carregar('CORPUS-COMMENTS.json')
    todos = _juntar(anterior, fora, 'COMMENT_ID')
    cc.gravar('CORPUS-COMMENTS.json', {
        'CAPTURED_AT': coletor.agora(),
        'WHAT_THIS_IS': 'AMOSTRA de comentários públicos dos materiais mais '
                        'relevantes. Não é censo e não é incidência de campo.',
        'LAW': cc.COMENTARISTA_NAO_E,
        'COMMENTS_TOTAL': len(todos),
        'BY_CLASS': dict(Counter(c['CLASS'] for c in todos)),
        'BY_ENTITY': resumo,
        'COMMENTS': todos})


def _peso_tecnico(m):
    """Quantos sinais de proteção de cultivo o texto do material carrega."""
    texto = (m.get('TEXT') or '') + ' ' + (m.get('TITLE') or '')
    return sum(1 for p in SINAIS_TECNICOS if cc.contem_palavra(texto, p))


SINAIS_TECNICOS = (
    # ES
    'plaga', 'hongo', 'enfermedad', 'malas hierbas', 'herbicida', 'fungicida',
    'insecticida', 'tratamiento', 'aplicación', 'aplicacion', 'repilo',
    'mildiu', 'oidio', 'trips', 'pulgón', 'pulgon', 'mosca', 'araña',
    # FR
    'maladie', 'ravageur', 'fongicide', 'herbicide', 'insecticide',
    'traitement', 'désherbage', 'desherbage', 'septoriose', 'pulvérisation',
    # IT
    'malattia', 'parassita', 'fungicida', 'diserbo', 'trattamento',
    'peronospora', 'oidio', 'insetticida',
)


# ═══════════════════════════════════════════════════ persistência
def _dias(data):
    from datetime import datetime, timezone
    if not data or len(data) < 10:
        return None
    try:
        d = datetime.strptime(data[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - d).days


def _resumo_canal(e, novos, man):
    from collections import Counter
    janelas = Counter(m['RECENCY_WINDOW'] for m in novos)
    return {
        'ENTITY_ID': e['ENTITY_ID'], 'HANDLE': e['HANDLE'],
        'PLATFORM': e['PLATFORM'], 'RUN_STATUS': man['STATUS'],
        'COST_USD': man['COST_USD'],
        'N_MATERIALS': len(novos),
        # §3 · o N real, sempre. Corpus curto é um fato do canal, não um defeito
        # a esconder — e o alvo NÃO vira régua por ter sido atingido.
        'DEPTH_TARGET': ALVO_POR_CANAL,
        'DEPTH_STATE': ('TARGET_MET' if len(novos) >= ALVO_MINIMO_DESEJADO
                        else 'BELOW_TARGET_N_REPORTED_AS_IS'),
        'BY_WINDOW': dict(janelas),
        'AS_OF_DATE': coletor.agora()[:10],
    }


def _juntar(anterior, novos, chave):
    idx = {r.get(chave): r for r in anterior if isinstance(r, dict)}
    for r in novos:
        idx[r.get(chave)] = r
    return [idx[k] for k in sorted(idx, key=lambda x: str(x))]


def _persistir(materiais, resumo, plataforma):
    from collections import Counter
    anterior = cc.carregar('CORPUS-MATERIALS.json')
    todos = _juntar(anterior, materiais, 'CONTENT_ID')
    defeitos = []
    for m in todos:
        defeitos.extend('%s · %s' % (m.get('CONTENT_ID'), d) for d in cc.checar(m))
    antigos = []
    caminho = os.path.join(cc.BASE, 'CORPUS-MATERIALS.json')
    if os.path.exists(caminho):
        with open(caminho, encoding='utf-8') as f:
            antigos = json.load(f).get('BY_CHANNEL') or []
    porcanal = _juntar(antigos, resumo, 'ENTITY_ID')
    cc.gravar('CORPUS-MATERIALS.json', {
        'CAPTURED_AT': coletor.agora(),
        'LAST_PHASE': plataforma,
        'WHAT_THIS_IS': 'MATERIAL público coletado dos canais provados. '
                        'Não é identidade, não é atividade canônica.',
        'DEPTH_LAW': 'N=30 é ALVO de profundidade, não régua. CONTENT_RATE_MIN_N '
                     'continua PROPOSAL_ONLY — chegar a 30 não publica taxa.',
        'WINDOW_LAW': 'janelas separadas. Material antigo prova HISTÓRICO, '
                      'nunca CURRENT_ACTIVITY.',
        'MATERIALS_TOTAL': len(todos),
        'BY_PLATFORM': dict(Counter(m['PLATFORM'] for m in todos)),
        'BY_WINDOW': dict(Counter(m['RECENCY_WINDOW'] for m in todos)),
        'BY_TEXT_COMPLETENESS': dict(Counter(m['TEXT_COMPLETENESS'] for m in todos)),
        'CONTRACT_DEFECTS': defeitos[:40],
        'CONTRACT_DEFECTS_TOTAL': len(defeitos),
        'BY_CHANNEL': porcanal,
        'MATERIALS': todos})


FASES = {'contratos': contratos, 'instagram': instagram, 'youtube': youtube,
         'comentarios': comentarios}

if __name__ == '__main__':
    fase = sys.argv[1] if len(sys.argv) > 1 else 'contratos'
    if fase not in FASES:
        print('fase desconhecida: %s · disponíveis: %s'
              % (fase, ', '.join(FASES))); raise SystemExit(1)
    with escopo_da_missao():
        FASES[fase]()
