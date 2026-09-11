#!/usr/bin/env python3
"""
COLETA DA COMUNICAÇÃO PÚBLICA DO CONCORRENTE — só sobre conta autorizada.

    py coleta/comunicacao_coleta.py contratos        # GRÁTIS: lê o schema dos atores
    py coleta/comunicacao_coleta.py posts YOUTUBE    # posts das contas autorizadas
    py coleta/comunicacao_coleta.py posts INSTAGRAM
    py coleta/comunicacao_coleta.py posts FACEBOOK

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
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
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
# A casa ja tem esta palavra em `leis/artefato.py`, e ela quer dizer outra
# coisa: o campo nao se aplica a este objeto. Nao e ignorancia — e ausencia
# de pergunta.
NAO_SE_APLICA = 'NAO_SE_APLICA'

JANELA_INICIAL_DIAS = 30
JANELA_AMPLIADA_DIAS = 90
CORPUS_BAIXO = 5               # itens por conta abaixo disto autorizam ampliar para 90

# Identificadores de ator. NENHUM foi executado por esta missão — `contratos` é quem
# troca esta marca por evidência. O YouTube reusa o ator que a Espanha já rodou com
# sucesso; os outros dois são candidatos e estão declarados como tal.
ATORES = {
    # O YouTube SAIU daqui na C3. Ele agora pede CAPACIDADE ao SINTONIA SCRAP, e
    # quem escolhe adaptador e fornecedor e o SCRAP — nao este ficheiro.
    'INSTAGRAM': ('apify~instagram-scraper', 'NAO_VERIFICADO'),
    'FACEBOOK': ('apify~facebook-posts-scraper', 'NAO_VERIFICADO'),
    'LINKEDIN': ('harvestapi~linkedin-post-search', 'JA_RODOU_NESTA_CASA'),
}

# ── A TABELA QUE SUBSTITUI O ATOR, E POR QUE ELA E DE CAPACIDADE ─────────────
# Uma plataforma que esta aqui NAO passa pela porta paga. Ela pede uma
# capacidade ao executor do SCRAP, e o SCRAP resolve a rota.
#
#     QUEM PEDE DIZ O QUE QUER. NUNCA DIZ COM QUE FERRAMENTA.
#
# Acrescentar o LinkedIn amanha e acrescentar uma LINHA aqui — nao e escrever um
# `if plataforma ==` neste ficheiro. Este ficheiro nao pode virar um segundo
# roteador, e a diferenca entre as duas coisas e exatamente esta tabela.
CAPACIDADES_SCRAP = {
    'YOUTUBE': {'RESOLVER': 'youtube.channel.resolve',
                'COLHER': 'youtube.channel.discovery'},
}


def _PLATAFORMAS():
    """As plataformas que esta fase atende, venham de que rota vierem.

    Duas tabelas, uma pergunta. Enquanto so havia `ATORES`, ela respondia
    sozinha; depois da C3 ha plataformas sem ator nenhum, e continuar a
    perguntar so a `ATORES` faria o YouTube desaparecer do proprio CLI.
    """
    return set(ATORES) | set(CAPACIDADES_SCRAP)


def contas_autorizadas(plataforma=None):
    """As contas do LOTE CONGELADO. Este arquivo não decide quem entra — ele obedece."""
    if not os.path.exists(LOTE):
        raise SystemExit(
            'sem lote congelado. Rode `py regras/comunicacao_lote.py` antes.\n'
            'A coleta paga não improvisa a lista: ela obedece a uma lista datada.')
    with open(LOTE, encoding='utf-8') as f:
        d = json.load(f)
    cs = d['ACCOUNTS']
    if plataforma:
        cs = [c for c in cs if c['PLATFORM'] == plataforma]
    return cs


def _gravar(nome, corpo):
    """Escreve, e devolve o caminho REAL — nao um caminho decorado.

    Ele devolvia sempre `data/samples/COMPETITOR-PUBLIC-COMM/<nome>`, mesmo
    quando `SAIDA` apontava para outro sitio. A mensagem dizia uma coisa e o
    disco fazia outra, e quem lesse o log procuraria o ficheiro onde ele nao
    estava.

        UM CAMINHO IMPRESSO QUE NAO E O CAMINHO ESCRITO E UMA PISTA FALSA.
    """
    os.makedirs(SAIDA, exist_ok=True)
    destino = os.path.join(SAIDA, nome)
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return os.path.relpath(destino, ROOT) if destino.startswith(ROOT) else destino


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
       `ferramentas/contrato_ator.py`, que lê o `inputSchema` do build e confere a entrada
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
    # O YouTube SAIU daqui na C3, e a ausencia e a prova. Esta funcao monta a
    # ENTRADA DE UM ATOR; o YouTube deixou de ter ator, entao deixou de ter
    # entrada. Manter o bloco «por via das duvidas» deixaria codigo morto com
    # cara de rota viva, e daqui a tres meses alguem o ligaria de volta sem
    # perceber que a rota paga tinha sido aposentada.
    #
    #     CODIGO MORTO COM CARA DE ROTA VIVA E PIOR QUE CODIGO APAGADO.
    #
    # Pedir entrada de ator para o YouTube agora levanta, e a mensagem diz
    # exatamente onde ir buscar a rota certa.
    if plataforma == 'INSTAGRAM':
        return {'directUrls': [url], 'resultsType': 'posts', 'resultsLimit': 50,
                'onlyPostsNewerThan': desde}
    if plataforma == 'FACEBOOK':
        return {'startUrls': [{'url': url}], 'resultsLimit': 50,
                'onlyPostsNewerThan': desde}
    if plataforma == 'LINKEDIN':
        return {'companyUrls': [url], 'maxItems': 50, 'postedLimit': '%dd' % dias}
    if plataforma in CAPACIDADES_SCRAP:
        raise ValueError(
            '%s nao tem entrada de ator: ela pede CAPACIDADE ao SINTONIA SCRAP '
            '(%s). Ver `_colher_pelo_scrap`.'
            % (plataforma, ', '.join(sorted(CAPACIDADES_SCRAP[plataforma].values()))))
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
        # Os nomes em MAIUSCULA sao os do envelope do SCRAP; os minusculos,
        # os do ator pago. Os dois convivem de proposito: a mesma coleta pode
        # vir de uma rota ou da outra, e o item nao muda de forma por causa
        # disso. Converter um no outro antes de normalizar seria disfarcar a
        # origem — e a origem e exatamente o que tem de ficar legivel.
        'POST_ID': g('NATIVE_ID', 'id', 'videoId', 'postId', 'shortCode', 'url'),
        'ACCOUNT_ID': conta['ACCOUNT_HANDLE'],
        'ACCOUNT_URL': conta['ACCOUNT_URL'],
        'COMPANY': conta['COMPANY'],
        'COUNTRY_SCOPE': conta['COUNTRY'],
        # ── UM CAMPO QUE O LOTE NUNCA TEVE ──────────────────────────────
        # Medido ao migrar: NENHUMA das 22 contas do lote congelado carrega
        # `ACCOUNT_SCOPE`. Nem uma. O acesso direto levantava `KeyError` na
        # PRIMEIRA conta, de qualquer plataforma — o que diz, sozinho, que esta
        # normalizacao nunca correu ate ao fim desde que o lote foi congelado.
        #
        #     UM `KeyError` NA PRIMEIRA CONTA NAO E UM CASO RARO. E a prova de
        #     que o caminho nunca passou por aqui.
        #
        # `regras/comunicacao_universo.py` escreve o campo com `NOT_KNOWN` no
        # ficheiro do universo, entao o valor honesto e esse mesmo. Trocar por
        # `PAGE_ROLE` seria mais bonito e seria outra coisa: papel da pagina nao
        # e alcance da conta.
        'ACCOUNT_SCOPE': conta.get('ACCOUNT_SCOPE', NAO_SEI),
        'PLATFORM': plataforma,
        'PUBLISHED_AT': g('PUBLISHED_AT', 'date', 'publishedAt', 'timestamp', 'time'),
        'FIRST_OBSERVED': _hoje().isoformat(),
        'LAST_OBSERVED': _hoje().isoformat(),
        'URL': g('URL', 'url', 'postUrl', 'link'),
        'TITLE': g('TITLE', 'title', 'headline'),
        # `TEXT` E A LEGENDA — o que o autor escreveu. Fica dito aqui porque, a
        # partir de 2026-09-10, existe um segundo texto no mesmo item: a FALA.
        # Somar os dois neste campo apagaria qual deles sustentou o que vier
        # depois. A fala entra em `TRANSCRIPT_TEXT`, e nunca aqui.
        'TEXT': g('TEXT', 'text', 'caption', 'description', 'content'),
        'TEXT_KIND': 'CAPTION',
        'MEDIA_TYPE': g('CONTENT_TYPE', 'type', 'mediaType', 'productType'),
        # ── O ENDERECO DO VIDEO, QUE ATE AQUI SE PERDIA ─────────────────────
        # A normalizacao deitava fora o endereco da midia. Sem ele, um Reel
        # coletado (e pago) nao podia ser ouvido depois sem se coletar outra
        # vez — e coletar outra vez custa. O endereco e ASSINADO e MORRE em
        # horas; guarda-lo nao e preserva-lo, e por isso o campo diz TEMPORARY.
        #
        #     ENDERECO VENCIDO != VIDEO INEXISTENTE.
        'MEDIA_URL_TEMPORARY': g('videoUrl', 'video_url', 'videoUrlBackup',
                                 'displayUrl', 'mediaUrl'),
        'MEDIA_DURATION_S': g('videoDuration', 'duration', 'durationSeconds'),
        'IS_VIDEO': ('YES' if str(g('CONTENT_TYPE', 'type', 'mediaType',
                                    'productType')).upper()
                     in ('VIDEO', 'REEL', 'CLIPS', 'IGTV') else NAO_SEI),
        # A FALA AINDA NAO FOI PEDIDA. Nascer NOT_REQUESTED, e nao vazio, e o
        # que impede «ninguem transcreveu» de se ler como «nao havia fala».
        'TRANSCRIPT_TEXT': None,
        'TRANSCRIPT_STATE': 'NOT_REQUESTED',
        'COLLECTION_WINDOW_DAYS': dias,
        'COLLECTION_WINDOW_FROM': _desde(dias),
        'DATASET_OWNER': DATASET_OWNER,
        # A cadeia CONTENT -> RUN_ID -> MANIFEST -> RAW fecha aqui, no item.
        'COLLECTION_RUN_ID': man.get('RUN_ID', NAO_SEI),
        'RAW_REFERENCE': man.get('RAW_EVIDENCE_PATH',
                                 bruto.get('RAW_REFERENCE', NAO_SEI)),
        'RAW_COMPLETENESS': man.get('RAW_COMPLETENESS', NAO_SEI),
        # ── QUEM TROUXE ISTO, E A VERDADE NAO E SEMPRE «UM ATOR» ────────
        # Enquanto so havia rota paga, `ACTOR` respondia a pergunta inteira.
        # Agora ha itens que vieram da API oficial, e para esses nao existe
        # ator nenhum. Escrever `NOT_KNOWN` seria dizer «nao sei qual ator»,
        # que e falso: sei que nao houve.
        #
        #     NAO_SE_APLICA E NAO_SEI SAO RESPOSTAS DIFERENTES.
        'ACTOR': man.get('ACTOR') or NAO_SE_APLICA,
        'COLLECTION_PROVIDER': man.get('COLLECTION_PROVIDER', NAO_SEI),
        'MISSION': MISSION,
        'RUNNER_NAME': RUNNER,
    }


def _gravar_posts(plataforma, contas, janela, r, mans, ampliou):
    """O artefato da fase. UM formato so, venha o item de que rota vier.

    Duas funcoes a escrever o mesmo ficheiro divergiriam no terceiro mes, e a
    divergencia apareceria como «o YouTube tem campos a menos».
    """
    pagas = [m for m in mans if m.get('PAID')]
    quota = sum(m.get('OFFICIAL_API_QUOTA_USED') or 0 for m in mans)
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
        # ── TRES NUMEROS, E ELES NAO SAO O MESMO NUMERO ──────────────────────
        # `APIFY_RUNS` contava TODA corrida enquanto toda corrida era paga.
        # Agora ha corridas gratuitas, e manter a conta antiga faria a rota
        # oficial aparecer como gasto no relatorio de custo.
        #
        #     APIFY_RUNS = NUMERO DE CHAMADAS DA API OFICIAL SERIA FALSO.
        #
        # O campo legado sobrevive porque ha leitor real — `comunicacao_medir`
        # — e passa a contar so o que foi PAGO. Para uma fase inteiramente
        # oficial ele vale 0, e o zero e verdadeiro.
        'COLLECTION_RUNS': len(mans),
        'APIFY_RUNS': len(pagas),
        'OFFICIAL_API_QUOTA_USED': quota,
        'COLLECTION_PROVIDERS': sorted({m.get('COLLECTION_PROVIDER') for m in mans
                                        if m.get('COLLECTION_PROVIDER')}),
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


def _colher_pelo_scrap(plataforma, contas, dias):
    """A colheita pela rota canonica. → (itens, manifestos).

    Sem pool de chaves, sem token, sem rotacao: nao ha chave paga para rodar. O
    que ha e uma capacidade pedida ao executor, e o executor escolhe a rota.

        ESTE FICHEIRO NAO SABE O QUE E `yt-dlp`, `channels.list` OU APIFY.
        Ele sabe que quer a comunicacao publica de uma conta. Mais nada.

    Cada conta produz UM registo de corrida, e esse registo diz quem trouxe. Um
    manifesto que nao diz o fornecedor obriga quem le a adivinhar — e quem
    adivinha escreve «Apify» por habito.
    """
    import scrap_executor as scrap
    caps = CAPACIDADES_SCRAP[plataforma]
    itens, mans = [], []
    for conta in contas:
        rid = '%s-%s-%s-%s' % (MISSION, plataforma, conta['COMPANY'], conta['COUNTRY'])
        man = {'RUN_ID': rid, 'PLATFORM': plataforma, 'ACTOR': None,
               'COLLECTION_PROVIDER': None, 'PAID': False, 'COST_USD': 0.0,
               'OFFICIAL_API_QUOTA_USED': 0, 'ACCOUNT_URL': conta['ACCOUNT_URL'],
               'STATUS': None, 'CAPTURED_AT': coletor.agora()}

        alvo, trace_r = scrap.COLLECT(platform=plataforma, capability=caps['RESOLVER'],
                                      run_id=rid, country_scope=conta['COUNTRY'],
                                      account_url=conta['ACCOUNT_URL'])
        man['OFFICIAL_API_QUOTA_USED'] += trace_r.get('QUOTA_UNITS') or 0
        man['COLLECTION_PROVIDER'] = trace_r.get('PROVIDER_USED')
        if not alvo:
            # NAO RESOLVER NAO E COLETAR ZERO. O estado sobe inteiro para que
            # ninguem leia «esta empresa nao publica» onde a verdade e «este
            # endereco nao tem resolvedor oficial».
            man['STATUS'] = trace_r.get('RESULT')
            man['TRACE'] = trace_r
            mans.append(man)
            continue

        objetos, trace_c = scrap.COLLECT(
            platform=plataforma, capability=caps['COLHER'], run_id=rid,
            country_scope=conta['COUNTRY'], channel_id=alvo[0]['CHANNEL_ID'],
            limit=50)
        man['STATUS'] = trace_c.get('RESULT')
        man['COLLECTION_PROVIDER'] = trace_c.get('PROVIDER_USED') or man['COLLECTION_PROVIDER']
        man['PAID'] = bool(trace_c.get('PAID_PROVIDER_USED'))
        man['OFFICIAL_API_QUOTA_USED'] += 1
        man['CHANNEL_ID'] = alvo[0]['CHANNEL_ID']
        man['TRACE'] = trace_c
        mans.append(man)
        itens.extend(normalizar(o, conta, plataforma, dias, man) for o in objetos)
    return itens, mans


def fase_posts(plataforma):
    contas = contas_autorizadas(plataforma)
    if not contas:
        print('nenhuma conta AUTORIZADA em %s. Isto é ausência de conta provada '
              'LOCAL — não é ausência de comunicação.' % plataforma)
        return None

    janela = {'DIAS': JANELA_INICIAL_DIAS}
    mans = []

    # ── A BIFURCACAO E POR TABELA, NAO POR NOME DE PLATAFORMA ────────────────
    # Um `if plataforma == 'YOUTUBE'` aqui faria deste ficheiro um segundo
    # roteador, e o proximo a migrar acrescentaria o segundo `elif`. A pergunta
    # certa nao e «qual plataforma e esta» — e «esta plataforma ja tem
    # capacidade canonica?».
    if plataforma in CAPACIDADES_SCRAP:
        itens, mans = _colher_pelo_scrap(plataforma, contas, janela['DIAS'])
        r = {'ITEMS': itens, 'UNITS_DONE': [c['ACCOUNT_URL'] for c in contas],
             'UNITS_PENDING': [], 'STATE': 'DONE', 'DUPLICATES_REMOVED': 0}
        ampliou = 'NO'
        return _gravar_posts(plataforma, contas, janela, r, mans, ampliou)

    ator, _ = ATORES[plataforma]

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
        # A rota paga DECLARA que foi paga. Antes ninguem precisava: tudo era
        # pago. Agora que ha duas, quem nao se declara obriga o contador a
        # adivinhar — e adivinhar aqui e escrever «Apify» por habito.
        man['PAID'] = True
        man.setdefault('COLLECTION_PROVIDER', 'APIFY')
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

    return _gravar_posts(plataforma, contas, janela, r, mans, ampliou)


def fase_transcrever(plataforma, run_id=None, teto=None):
    """A FALA DOS VIDEOS JA COLETADOS. Nenhuma execucao paga nova acontece aqui.

    POR QUE ESTA FASE VIVE NESTE FICHEIRO, E NAO NOUTRO
    ----------------------------------------------------
    Porque o orquestrador ja conhece este executor (T9), e a receita ja traduz
    `fase` e `plataforma` do pedido em argumentos da linha de comando. Registar
    um executor novo criaria uma segunda porta para a mesma capacidade — e o
    orquestrador so chama o PRIMEIRO executor de cada alvo, portanto a segunda
    porta nunca seria aberta e ficaria a mentir no registo.

        O BOTAO PEDE. O ORQUESTRADOR DECIDE COMO. UMA CAPACIDADE, UMA PORTA.

    O trabalho em si nao e daqui: e de `ferramentas/reel_transcricao.py`, que e
    a cadeia, e de `ferramentas/fala_local.py`, que e o reconhecedor. Esta
    funcao so leva o pedido ate la.
    """
    import reel_transcricao as rt
    return rt.fase_posts(plataforma, teto=teto, run_id=run_id)


if __name__ == '__main__':
    fase = sys.argv[1] if len(sys.argv) > 1 else 'contratos'
    resto = [a for a in sys.argv[2:] if not a.startswith('--')]
    op = dict(a[2:].split('=', 1) for a in sys.argv[2:]
              if a.startswith('--') and '=' in a)
    if fase == 'contratos':
        fase_contratos()
    elif fase == 'posts':
        if not resto or resto[0] not in _PLATAFORMAS():
            print('uso: comunicacao_coleta.py posts {%s}'
                  % '|'.join(sorted(_PLATAFORMAS())))
            raise SystemExit(2)
        fase_posts(resto[0])
    elif fase == 'transcrever':
        if not resto or resto[0] not in _PLATAFORMAS():
            print('uso: comunicacao_coleta.py transcrever {%s}'
                  % '|'.join(sorted(_PLATAFORMAS())))
            raise SystemExit(2)
        raise SystemExit(fase_transcrever(resto[0], run_id=op.get('run-id'),
                                          teto=op.get('teto')))
    else:
        print('fase desconhecida: %s' % fase)
        raise SystemExit(2)
