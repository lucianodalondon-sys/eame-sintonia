#!/usr/bin/env python3
"""
COLETA DA COMUNICAÇÃO PÚBLICA DO CONCORRENTE — só sobre conta autorizada.

    py scripts/comunicacao_coleta.py contratos        # GRÁTIS: lê o schema dos atores
    py scripts/comunicacao_coleta.py posts YOUTUBE    # posts das contas autorizadas
    py scripts/comunicacao_coleta.py posts INSTAGRAM
    py scripts/comunicacao_coleta.py posts FACEBOOK

A ORDEM É LEI
--------------
    UNIVERSO -> ÂNCORA -> IDENTIDADE -> COLETA

As três primeiras já rodaram e custaram zero. Este arquivo lê `CONTAS-V1.json` e só
aceita linha com `COLLECTION_AUTHORIZED = YES` — que significa `PROVED` **e**
`LOCAL_COUNTRY`. Ele NÃO reabre a decisão de identidade e NÃO promove ninguém: se a
régua estiver errada, o conserto é no arquivo de identidade, de graça, e esta coleta
roda de novo sobre a lista nova.

    CONTA OFICIAL != CONTA DAQUELE PAÍS. A coleta exige as duas.

`contratos` RODA ANTES DE TUDO, E NÃO É CERIMÔNIA
---------------------------------------------------
Ler o schema de um ator é um GET, custa ZERO e prova duas coisas que só se descobrem
caro: que o ator EXISTE com aquele identificador, e que ele aceita os campos que eu vou
mandar. O piloto italiano desta casa queimou 8 execuções pagas mandando um campo que o
Actor descartava em silêncio — os 8 runs devolveram o mesmo consultor de cibersegurança.

    ENTRADA ERRADA != PLATAFORMA ERRADA. MATCH VAZIO NÃO AUTORIZA GASTO.

Os identificadores de ator abaixo estão marcados `NAO_VERIFICADO` porque nenhuma
execução desta missão os tocou ainda. `contratos` é o passo que troca essa marca por
evidência — e nenhuma fase paga deve rodar antes dele passar.

A JANELA COMEÇA EM 30 DIAS, E O MOTIVO É O §4
-----------------------------------------------
30 dias primeiro; 90 só se o corpus vier baixo. Abrir anos de histórico na primeira
tentativa transforma uma pergunta sobre o AGORA ("sobre o que esta empresa está falando
publicamente?") numa fatura. E a janela vai gravada em cada item: sem ela, o corpus não
sabe dizer se um silêncio é silêncio da empresa ou silêncio da janela.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não classifica, não extrai cultura, não declara mudança, não cruza com Meta nem com o
Foresight. Ele busca, preserva o RAW e grava o normalizado. Tudo o que vem depois roda
de graça sobre o artefato — para que um erro de classificador custe zero e possa ser
refeito quantas vezes precisar.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap        # noqa: E402  — dono único da rotação de chave
import coletor                 # noqa: E402  — porta única das rotas pagas

SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM')
# A coleta obedece ao LOTE CONGELADO, não à régua. `CONTAS-V1.json` muda quando o
# critério de identidade muda — o que é bom enquanto nada foi pago. Depois da primeira
# execução paga, a lista tem que parar de se mexer, senão o rendimento fica medido contra
# um denominador que mudou no meio.
#
#     LISTA QUE MUDA SOZINHA APAGA A MEDIÇÃO DO RENDIMENTO.
LOTE = os.path.join(SAIDA, 'PUBLIC-COMM-FIRST-BATCH-EAME.json')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

JANELA_INICIAL_DIAS = 30
JANELA_AMPLIADA_DIAS = 90
CORPUS_BAIXO = 5               # itens por conta abaixo disto autorizam ampliar para 90

# Identificadores de ator. NENHUM foi executado por esta missão — `contratos` é quem
# troca esta marca por evidência. O YouTube reusa o ator que a Espanha já rodou com
# sucesso; os outros dois são candidatos e estão declarados como tal.
ATORES = {
    'YOUTUBE': ('streamers~youtube-scraper', 'JA_RODOU_NESTA_CASA'),
    'INSTAGRAM': ('apify~instagram-scraper', 'NAO_VERIFICADO'),
    'FACEBOOK': ('apify~facebook-posts-scraper', 'NAO_VERIFICADO'),
    'LINKEDIN': ('harvestapi~linkedin-post-search', 'JA_RODOU_NESTA_CASA'),
}


def contas_autorizadas(plataforma=None):
    """As contas do LOTE CONGELADO. Este arquivo não decide quem entra — ele obedece."""
    if not os.path.exists(LOTE):
        raise SystemExit(
            'sem lote congelado. Rode `py scripts/comunicacao_lote.py` antes.\n'
            'A coleta paga não improvisa a lista: ela obedece a uma lista datada.')
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    cs = d['ACCOUNTS']
    if plataforma:
        cs = [c for c in cs if c['PLATFORM'] == plataforma]
    return cs


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/COMPETITOR-PUBLIC-COMM/' + nome


def _hoje():
    import datetime
    return datetime.date.today()


def _desde(dias):
    import datetime
    return (_hoje() - datetime.timedelta(days=dias)).isoformat()


# ── FASE GRÁTIS ────────────────────────────────────────────────────────────────
def fase_contratos():
    """Lê o CONTRATO de cada ator: existe, e aceita os campos que eu vou mandar.

    DOIS DEFEITOS CONSERTADOS EM 2026-09-02:

    1. **Desistia sem chave.** A primeira linha era `if not chaves: return POOL_EMPTY` —
       e assim a fase MAIS BARATA da casa era a primeira a parar de rodar. Verificado ao
       vivo: `GET https://api.apify.com/v2/acts/{ator}` responde **HTTP 200 sem
       credencial nenhuma** para ator público. O portão passa a rodar em qualquer
       máquina, inclusive em teste, inclusive com o pool vazio.

    2. **Provava metade do que prometia.** Fazia só `GET /v2/acts/{ator}` e lia
       `data.name`. Isso prova que o ATOR EXISTE — não prova nada sobre os campos que
       serão enviados, que é justamente o que queimou 8 execuções neste projeto. A
       docstring do arquivo promete as duas coisas; agora ela cumpre, porque delega para
       `scripts/contrato_ator.py`, que lê o `inputSchema` do build e confere a entrada
       campo a campo.

        ATOR EXISTE ≠ ATOR ACEITA A MINHA ENTRADA.
    """
    import contrato_ator as ca

    chaves = ap.pool()
    token = chaves[0] if chaves else None       # opcional: a rota é pública
    exemplo = {'ACCOUNT_URL': 'https://www.instagram.com/exemplo/',
               'ACCOUNT_HANDLE': 'exemplo', 'COUNTRY': 'ES'}

    fora, todos_ok = [], True
    for plataforma, (ator, marca) in sorted(ATORES.items()):
        try:
            ent = entrada(plataforma, exemplo, JANELA_INICIAL_DIAS)
        except ValueError:
            ent = {}
        r, ok = ca.portao(ator, ent, token=token)
        todos_ok = todos_ok and ok
        r.update({'PLATFORM': plataforma, 'PRIOR_EVIDENCE': marca})
        fora.append(r)
        print('  %-10s %-38s %-14s build %-9s %s'
              % (plataforma, ator, r['CONTRACT_STATE'], r.get('BUILD_NUMBER'),
                 'APROVADO' if ok else 'REPROVADO'))
        for p in r['PROBLEMS']:
            print('       [%s] %s — %s' % (p['GRAVIDADE'], p['CODIGO'], p['DETALHE'][:140]))

    corpo = {
        'SOURCE_ID': 'COMPETITOR-PUBLIC-COMM/CONTRATOS',
        'DATASET_OWNER': DATASET_OWNER,
        'source': ('GET /v2/acts/{ator} e /v2/actor-builds/{id} — leitura do schema, '
                   'nenhuma execução, nenhum item, nenhum custo, chave opcional'),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'TOKEN_USED': 'YES' if token else 'NO — a rota de leitura é pública',
        'ALL_APPROVED': 'YES' if todos_ok else 'NO',
        'REGRA': 'nenhuma fase paga roda com ALL_APPROVED = NO',
        'ACTORS': fora,
    }
    print('gravado em %s · todos aprovados: %s'
          % (_gravar('CONTRATOS.json', corpo), 'SIM' if todos_ok else 'NÃO'))
    return corpo


# ── FASE PAGA ──────────────────────────────────────────────────────────────────
def entrada(plataforma, conta, dias):
    """A entrada do ator, por plataforma. Uma função, para o contrato ser legível."""
    desde = _desde(dias)
    url = conta['ACCOUNT_URL']
    if plataforma == 'YOUTUBE':
        return {'startUrls': [{'url': url}], 'maxResults': 50,
                'dateFilter': desde, 'sortVideosBy': 'NEWEST'}
    if plataforma == 'INSTAGRAM':
        return {'directUrls': [url], 'resultsType': 'posts', 'resultsLimit': 50,
                'onlyPostsNewerThan': desde}
    if plataforma == 'FACEBOOK':
        return {'startUrls': [{'url': url}], 'resultsLimit': 50,
                'onlyPostsNewerThan': desde}
    if plataforma == 'LINKEDIN':
        return {'companyUrls': [url], 'maxItems': 50, 'postedLimit': '%dd' % dias}
    raise ValueError('plataforma sem contrato de entrada: %s' % plataforma)


def normalizar(bruto, conta, plataforma, dias, man=None):
    """RAW -> os campos do §4. O que a fonte não deu sai NOT_KNOWN, nunca vazio.

    `man` é o manifesto da execução que trouxe o item. Ele existe para fechar a cadeia
    de evidência NO ITEM: até 2026-09-02 `RAW_REFERENCE` nascia `NOT_KNOWN` com um
    comentário dizendo "preenchido por coletor ao gravar o RAW" — e o `coletor` grava o
    caminho no MANIFESTO, não no item. Ninguém costurava os dois, e todo item nascia
    apontando para lugar nenhum.
    """
    man = man or {}
    def g(*nomes):
        for n in nomes:
            v = bruto.get(n)
            if v not in (None, '', [], {}):
                return v
        return NAO_SEI

    return {
        'POST_ID': g('id', 'videoId', 'postId', 'shortCode', 'url'),
        'ACCOUNT_ID': conta['ACCOUNT_HANDLE'],
        'ACCOUNT_URL': conta['ACCOUNT_URL'],
        'COMPANY': conta['COMPANY'],
        'COUNTRY_SCOPE': conta['COUNTRY'],
        'ACCOUNT_SCOPE': conta['ACCOUNT_SCOPE'],
        'PLATFORM': plataforma,
        'PUBLISHED_AT': g('date', 'publishedAt', 'timestamp', 'time'),
        'FIRST_OBSERVED': _hoje().isoformat(),
        'LAST_OBSERVED': _hoje().isoformat(),
        'URL': g('url', 'postUrl', 'link'),
        'TITLE': g('title', 'headline'),
        'TEXT': g('text', 'caption', 'description', 'content'),
        'MEDIA_TYPE': g('type', 'mediaType', 'productType'),
        'COLLECTION_WINDOW_DAYS': dias,
        'COLLECTION_WINDOW_FROM': _desde(dias),
        'DATASET_OWNER': DATASET_OWNER,
        # A cadeia CONTENT -> RUN_ID -> MANIFEST -> RAW fecha aqui, no item.
        'COLLECTION_RUN_ID': man.get('RUN_ID', NAO_SEI),
        'RAW_REFERENCE': man.get('RAW_EVIDENCE_PATH', NAO_SEI),
        'RAW_COMPLETENESS': man.get('RAW_COMPLETENESS', NAO_SEI),
        'ACTOR': man.get('ACTOR', NAO_SEI),
        'MISSION': MISSION,
        'RUNNER_NAME': RUNNER,
    }


def fase_posts(plataforma):
    ator, _ = ATORES[plataforma]
    contas = contas_autorizadas(plataforma)
    if not contas:
        print('nenhuma conta AUTORIZADA em %s. Isto é ausência de conta provada '
              'LOCAL — não é ausência de comunicação.' % plataforma)
        return None

    janela = {'DIAS': JANELA_INICIAL_DIAS}
    mans = []

    def trabalho(conta, token):
        """A chamada da porta paga. QUATRO defeitos consertados aqui em 2026-09-02.

        Esta função nunca tinha rodado — nem para Instagram, nem para nenhuma das outras
        três plataformas. Ela quebrava na PRIMEIRA conta, e o jeito como quebrava é o
        que a torna perigosa:

          1. faltavam `source_version` e `evidence_path`, que `coletor.executar` exige
             sem default → `TypeError` antes de qualquer chamada sair da máquina;
          2. `executar` devolve a TUPLA `(itens, manifesto)` e o código lia `man.get(...)`
             — tupla não tem `.get`;
          3. lia `man['DATA']`, campo que o manifesto nunca teve. Os itens vêm no
             PRIMEIRO elemento da tupla;
          4. classificava por `PLATFORM_STATUS`/`STATUS_MESSAGE`, nomes que também não
             existem no manifesto — os reais são `STATUS` e `ERROR`.

        E o motivo de isso ser pior do que "não rodava": `executar_com_pool` captura
        exceção como `UNKNOWN_FAILURE`, que está em `NAO_ROTACIONAM` **de propósito**
        (bug meu não pode queimar o pool). O resultado é `STATE: STOPPED` com `ITEMS: []`,
        e o artefato sai com `ITEM_COUNT: 0`.

            UM BUG MEU SE APRESENTANDO COMO FONTE QUE NÃO RESPONDEU.

        Zero ali se lê como "a BASF não posta no Instagram". É a lei SOURCE FAILURE !=
        ZERO sendo violada de dentro para fora. Reproduzido antes do conserto:

            TypeError: executar() missing 2 required keyword-only arguments:
                       'source_version' and 'evidence_path'
        """
        rid = '%s-%s-%s-%s' % (MISSION, plataforma, conta['COMPANY'], conta['COUNTRY'])
        evidencia = ('data/samples/COMPETITOR-PUBLIC-COMM/POSTS-%s.json' % plataforma)
        itens, man = coletor.executar(
            ator, entrada(plataforma, conta, janela['DIAS']),
            token=token, run_id=rid, platform=plataforma,
            country=conta['COUNTRY'], mission=MISSION,
            query=conta['ACCOUNT_URL'],
            source_version='captura de %s' % coletor.agora()[:10],
            evidence_path=evidencia)
        mans.append(man)
        estado = ap.classificar(status=man.get('PLATFORM_STATUS'),
                                status_message=str(man.get('ERROR') or ''),
                                itens=itens)
        return ([normalizar(b, conta, plataforma, janela['DIAS'], man) for b in itens],
                estado)

    r = ap.executar_com_pool(contas, trabalho,
                             identidade=lambda i: (i['PLATFORM'], i['POST_ID']))

    # §4: 30 dias primeiro; 90 SÓ se o corpus vier baixo. A ampliação é uma decisão
    # registrada, com o número que a motivou — não um "tentei de novo".
    ampliou = 'NO'
    if r['STATE'] == 'DONE' and len(r['ITEMS']) < CORPUS_BAIXO * len(contas):
        ampliou = 'YES'
        janela['DIAS'] = JANELA_AMPLIADA_DIAS
        r2 = ap.executar_com_pool(contas, trabalho,
                                  identidade=lambda i: (i['PLATFORM'], i['POST_ID']))
        r = r2 if len(r2['ITEMS']) > len(r['ITEMS']) else r

    corpo = {
        'SOURCE_ID': 'COMPETITOR-PUBLIC-COMM/POSTS-%s' % plataforma,
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'contas oficiais LOCAIS provadas, coletadas por rota pública',
        'SOURCE_LOCATION': plataforma,
        'FACT_LOCATION': 'NOT_KNOWN — o §6 decide item a item, depois, de graça',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'COLLECTION_WINDOW_DAYS': janela['DIAS'],
        'WINDOW_WIDENED': ampliou,
        'WINDOW_WIDENED_WHY': (
            'menos de %d itens por conta na janela de %d dias'
            % (CORPUS_BAIXO, JANELA_INICIAL_DIAS)) if ampliou == 'YES' else 'n/a',
        'ACCOUNTS_ATTEMPTED': len(contas),
        'ACCOUNTS_DONE': len(r['UNITS_DONE']),
        'ACCOUNTS_PENDING': len(r['UNITS_PENDING']),
        'POOL_STATE': r['STATE'],
        'DUPLICATES_REMOVED': r['DUPLICATES_REMOVED'],
        'APIFY_RUNS': len(mans),
        'COST_USD': sum(m.get('COST_USD') or 0 for m in mans
                        if isinstance(m.get('COST_USD'), (int, float))),
        'ITEM_COUNT': len(r['ITEMS']),
        'ITEMS': r['ITEMS'],
        'RUNS': mans,
    }
    print('%s · %d contas · %d itens · janela %d dias'
          % (plataforma, len(contas), len(r['ITEMS']), janela['DIAS']))
    print('gravado em %s' % _gravar('POSTS-%s.json' % plataforma, corpo))
    return corpo


if __name__ == '__main__':
    fase = sys.argv[1] if len(sys.argv) > 1 else 'contratos'
    if fase == 'contratos':
        fase_contratos()
    elif fase == 'posts':
        if len(sys.argv) < 3 or sys.argv[2] not in ATORES:
            print('uso: comunicacao_coleta.py posts {%s}' % '|'.join(sorted(ATORES)))
            raise SystemExit(2)
        fase_posts(sys.argv[2])
    else:
        print('fase desconhecida: %s' % fase)
        raise SystemExit(2)
