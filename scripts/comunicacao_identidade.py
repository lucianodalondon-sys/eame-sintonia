#!/usr/bin/env python3
"""
IDENTIDADE DA CONTA DO CONCORRENTE — quem entra na coleta, decidido de graça.

    py scripts/comunicacao_identidade.py

A MAIOR LEI DESTA MISSÃO
-------------------------
    CONCORRENTE CERTO + CANAL CERTO, ANTES DE QUALQUER COLETA.

Este arquivo roda sobre `ANCORAS-EVIDENCIA-V1.json` — leitura já feita, custo zero — e
pode ser refeito quantas vezes o critério mudar sem gastar um centavo. É a mesma
separação que o `sensor_canal_identidade.py` já usa nesta casa, pelo mesmo motivo: quando
eu errar a regra, o conserto tem que ser grátis.

TRÊS PERGUNTAS INDEPENDENTES, NUNCA UMA
-----------------------------------------
    1. A conta é OFICIAL da empresa?          -> ACCOUNT_IDENTITY_STATE
    2. A conta é DAQUELE PAÍS?                -> COUNTRY_SCOPE
    3. A conta é da EMPRESA ou de uma MARCA?  -> PAGE_ROLE

Colapsar quaisquer duas é o erro que a missão manda não cometer. A BASF Espanha declara,
no próprio site espanhol, o LinkedIn `/company/basf`. A conta é **oficial** (a 1 fecha) e
é **global** (a 2 reprova). Ler aquilo como atividade espanhola seria transformar o
comunicado de Ludwigshafen em movimento de mercado em Sevilha.

A terceira pergunta nasceu de um erro MEU, pego pela aba árbitra. Eu tinha só duas, e
escrevi a página `DEKALB France` como escopo `PRODUCT` — o que a fez aparecer no relatório
entre as contas "não locais". Ela É local: a página se chama "DEKALB France" e aponta para
bayer-agri.fr. Um campo só me obrigou a escolher qual verdade apagar, e eu apaguei a certa.

    LOCALIDADE PROVADA E PAPEL DE MARCA SÃO VERDADE AO MESMO TEMPO.
    PRODUCT NÃO É UM ESTADO DE PAÍS.

Só passa para a coleta quem responde SIM às TRÊS:

    COLLECTION_AUTHORIZED = (estado == PROVED) e (pais == LOCAL_COUNTRY_PROVED) e (papel == COMPANY)

O QUE PROVA "OFICIAL"
----------------------
O site oficial LOCAL da empresa declarar o link. É a primeira parte falando de si
própria — não é busca por nome, não é semelhança de handle.

    NAME_SIMILARITY != ACCOUNT_PROOF.

O QUE PROVA "DAQUELE PAÍS", E O QUE NÃO PROVA
-----------------------------------------------
O que prova: a IDENTIFICAÇÃO da conta (o handle, o slug) carregar marca de país
explícita — `SyngentaFrance`, `bayer4cropses`, `nufarmespana`, `syngentaitalia`.

O que NÃO prova, e cada um destes apareceu de verdade na leitura:

  · **o subdomínio de idioma.** `it.linkedin.com/company/bayer-cropscience` — o `it.`
    é a interface em italiano; a conta é `bayer-cropscience`, sem país. Ler `it.` como
    Itália é inferir país pela língua, que o §6 proíbe em letra.
  · **o parâmetro de idioma.** `/company/basf/?originalSubdomain=it` e
    `/basf_global/?hl=it` — o `?hl=it` é preferência de exibição, não dono da conta.
    E o segundo caso diz `global` no próprio handle.
  · **o site onde o link foi achado.** O site francês da Corteva declara
    `@CortevaBiologicals`, e o canal não nomeia país nenhum — o site onde o link
    aparece não prova o país da conta. (A `/dekalbfr` é o caso oposto e por isso
    instrutivo: ali o país está provado pela PRÓPRIA página, e o que a exclui é o
    papel de marca, medido em `PAGE_ROLE`.)

O QUE NEM CHEGA A SER CANDIDATO
---------------------------------
Três formas de ruído passaram pelo filtro de domínio e nenhuma é conta:

    facebook.com/policy.php            aviso do fornecedor de cookies (4 sites)
    youtube.com/watch?v=...            um vídeo
    youtube.com/playlist?list=...      uma playlist

Elas saem `REJECTED` com o motivo escrito, e não somem. Sumir seria pior: a BASF França
declara SÓ uma playlist, e um relatório que apagasse a linha diria "a BASF França não
declara nada" quando o certo é "declara uma playlist, que não é conta".

AUSÊNCIA DE LINK NÃO É AUSÊNCIA DE CONTA
------------------------------------------
`NOT_KNOWN` aqui significa **o site não declarou**. A Corteva Itália não declara nenhum
link social; isso não autoriza dizer que ela não tem conta nem que ela não comunica. É a
mesma lei que a casa já escreveu como `SOURCE FAILURE != ZERO`, aplicada à identidade.
"""
import json
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM')
EVIDENCIA = os.path.join(SAIDA, 'ANCORAS-EVIDENCIA-V1.json')

DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'
NAO_SEI = 'NOT_KNOWN'

PLATAFORMA_POR_DOMINIO = [
    ('linkedin.com', 'LINKEDIN'),
    ('youtube.com', 'YOUTUBE'),
    ('youtu.be', 'YOUTUBE'),
    ('instagram.com', 'INSTAGRAM'),
    ('facebook.com', 'FACEBOOK'),
]

# Caminhos que NÃO são conta. Lista fechada e comentada: cada entrada apareceu na leitura
# real dos 15 âncoras.
NAO_E_CONTA = [
    (r'^/policy\.php', 'aviso do fornecedor de cookies do Facebook, não é página de empresa'),
    (r'^/watch$', 'é um vídeo, não um canal'),
    (r'^/playlist$', 'é uma playlist, não um canal'),
    (r'^/privacy', 'página de política, não é conta'),
    (r'^/help', 'página de ajuda da plataforma, não é conta'),
    (r'^/?$', 'é a raiz da plataforma, sem conta identificada'),
]

# Marcas de país aceitas DENTRO da identificação da conta. Casam como palavra/segmento,
# nunca como pedaço solto: `es` dentro de "basf_global" não pode virar Espanha.
MARCAS_DE_PAIS = {
    'ES': ['es', 'esp', 'espana', 'españa', 'spain', 'iberia'],
    'IT': ['it', 'ita', 'italia', 'italy'],
    'FR': ['fr', 'fra', 'france', 'francia'],
}

# As marcas POR EXTENSO também casam GRUDADAS no fim do handle. Só estas, e o motivo é
# aritmético: `syngentaitalia` e `nufarmespana` não têm separador nem troca de caixa, e a
# régua de palavra inteira os reprovava. Uma palavra de 5+ letras colidir por acaso no
# fim de um handle é raro; `es`, `it` e `fr` colidirem é banal — "cropses", "credit",
# "surf" — e por isso as de DUAS LETRAS continuam valendo só como palavra inteira.
MARCAS_POR_EXTENSO = {
    'ES': ['espana', 'españa', 'spain', 'iberia'],
    'IT': ['italia', 'italy'],
    'FR': ['france', 'francia'],
}

# Marcas que declaram escopo NÃO-local no próprio identificador.
MARCAS_GLOBAIS = ['global', 'international', 'worldwide', 'official', 'corp', 'group']
MARCAS_REGIONAIS = ['europe', 'eu', 'emea', 'eame']


def plataforma_de(url):
    host = (urllib.parse.urlsplit(url).hostname or '').lower()
    for dominio, nome in PLATAFORMA_POR_DOMINIO:
        if host == dominio or host.endswith('.' + dominio):
            return nome
    return None


def _caminho(url):
    return urllib.parse.urlsplit(url).path or '/'


def nao_e_conta(url):
    """→ motivo, ou ''. Roda ANTES de qualquer leitura de handle."""
    p = _caminho(url).rstrip('/') or '/'
    for padrao, motivo in NAO_E_CONTA:
        if re.search(padrao, p, re.I):
            return motivo
    return ''


def identificador(url):
    """O HANDLE — a parte que identifica a conta. Sem host, sem query, sem idioma.

    O host inteiro é descartado de propósito: `it.linkedin.com` e `au.linkedin.com`
    apontam para a MESMA conta, e o prefixo é a interface, não o dono.
    """
    p = [t for t in _caminho(url).split('/') if t]
    # `company/`, `user/`, `c/`, `people/`, `@handle` — prefixos de rota da plataforma.
    ROTAS = {'company', 'user', 'c', 'channel', 'people', 'pages', 'showcase'}
    partes = [t for t in p if t.lower() not in ROTAS]
    if not partes:
        return ''
    return urllib.parse.unquote(partes[0]).lstrip('@')


def _fatias(handle):
    """Quebra o handle em pedaços comparáveis: separador, caixa e dígito."""
    h = urllib.parse.unquote(handle)
    h = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', h)          # BayerCropScienceEspaña
    h = re.sub(r'[^A-Za-zÀ-ÿ0-9]+', ' ', h)             # . _ - separam
    return [t.lower() for t in h.split() if t]


def escopo(handle, pais):
    """→ (COUNTRY_SCOPE, evidência). Decide pelo IDENTIFICADOR, nunca pelo site."""
    if not handle:
        return NAO_SEI, 'não foi possível ler um identificador de conta nesta URL'
    fatias = _fatias(handle)

    for marca in MARCAS_GLOBAIS:
        if marca in fatias:
            return 'GLOBAL', ('o próprio identificador "%s" declara "%s"'
                              % (handle, marca))
    for marca in MARCAS_REGIONAIS:
        if marca in fatias:
            return 'REGIONAL_EUROPE', ('o próprio identificador "%s" declara "%s"'
                                       % (handle, marca))

    do_pais = [m for m in MARCAS_DE_PAIS[pais] if m in fatias]
    if do_pais:
        return 'LOCAL_COUNTRY_PROVED', (
            'o identificador "%s" carrega marca de país explícita (%s) para %s'
            % (handle, ', '.join(do_pais), pais))

    grudado = ''.join(fatias)
    colada = [m for m in MARCAS_POR_EXTENSO[pais] if grudado.endswith(m)]
    if colada:
        return 'LOCAL_COUNTRY_PROVED', (
            'o identificador "%s" termina com o nome do país por extenso ("%s"), sem '
            'separador. Só nome por extenso vale grudado — "es"/"it"/"fr" no fim de '
            'palavra colidem à toa.' % (handle, colada[0]))

    outro = [(p, m) for p, ms in MARCAS_DE_PAIS.items() if p != pais
             for m in ms if m in fatias]
    if outro:
        return 'OTHER', (
            'o identificador "%s" carrega marca de OUTRO país (%s), não de %s'
            % (handle, ', '.join(sorted({p for p, _ in outro})), pais))

    return NAO_SEI, (
        'o identificador "%s" não carrega marca de país. Pode ser conta global, '
        'regional ou de produto — o link sozinho não decide, e assumir LOCAL aqui é '
        'exatamente o erro que o §1 proíbe.' % handle)


def resolver(ancora):
    """→ lista de contas resolvidas para um COMPANY x COUNTRY."""
    empresa, pais = ancora['COMPANY'], ancora['COUNTRY']
    ancora_ok = ancora.get('ANCHOR_SITE_STATE') == 'PROVED'
    fora, vistos = [], set()

    for link in ancora.get('DECLARED_LINKS') or []:
        url = link['HREF']
        plataforma = plataforma_de(url)
        if not plataforma:
            continue

        motivo = nao_e_conta(url)
        if motivo:
            fora.append(_linha(empresa, pais, plataforma, url, link,
                               handle='', estado='REJECTED', escopo_=NAO_SEI,
                               ev='não é conta: %s' % motivo, ev_escopo='n/a'))
            continue

        handle = identificador(url)
        if not handle:
            fora.append(_linha(empresa, pais, plataforma, url, link,
                               handle='', estado='REJECTED', escopo_=NAO_SEI,
                               ev='não é conta: a URL não traz identificador de conta',
                               ev_escopo='n/a'))
            continue

        # DEDUPE por PLATAFORMA + HANDLE. O mesmo site pode listar a conta duas vezes
        # (rodapé e cabeçalho); é UM objeto, nunca duas evidências.
        chave = (plataforma, handle.lower())
        if chave in vistos:
            continue
        vistos.add(chave)

        esc, ev_esc = escopo(handle, pais)
        if not ancora_ok:
            estado, ev = 'CANDIDATE', (
                'o link foi lido, mas o âncora (site oficial local) não está PROVED — '
                'sem âncora provado não há caminho de prova.')
        else:
            estado, ev = 'PROVED', (
                'o site oficial local de %s em %s (%s, título "%s") declara este link. '
                'Primeira parte falando de si própria — não é busca por nome.'
                % (empresa, pais, ancora['FINAL_URL'], ancora['PAGE_TITLE']))
        fora.append(_linha(empresa, pais, plataforma, url, link, handle,
                           estado, esc, ev, ev_esc))
    return fora


def _linha(empresa, pais, plataforma, url, link, handle, estado, escopo_, ev, ev_escopo,
           papel='COMPANY', ev_papel=None):
    """Uma linha de conta. TRÊS perguntas independentes, nunca colapsadas.

    A primeira versão deste arquivo tinha DUAS, e isso produziu um erro semântico que a
    aba árbitra pegou: a página `DEKALB France` saiu com escopo `PRODUCT`, e o relatório
    a listou entre as contas "não locais". Mas a localidade dela está PROVADA — a página
    se chama "DEKALB France" e aponta para bayer-agri.fr. O que a tira do lote não é o
    país; é o PAPEL.

        LOCALIDADE PROVADA E PAPEL DE MARCA PODEM SER VERDADE AO MESMO TEMPO.

    Um campo só forçava a escolher qual verdade apagar. Agora são três:

        ACCOUNT_IDENTITY_STATE   a conta é oficial da empresa?
        COUNTRY_SCOPE            a conta é daquele país?
        PAGE_ROLE                a conta é da EMPRESA ou de uma MARCA/PRODUTO?

    E a elegibilidade é a conjunção das três. `ELIGIBLE_FOR_COMPANY_LOCAL_BATCH = NO`
    passa a ter um motivo LEGÍVEL, em vez de virar "não é local" quando é.
    """
    razoes = []
    if estado != 'PROVED':
        razoes.append('a conta não está PROVED como oficial (%s)' % estado)
    if escopo_ != 'LOCAL_COUNTRY_PROVED':
        razoes.append('o país da conta não está provado como %s (COUNTRY_SCOPE=%s)'
                      % (pais, escopo_))
    if papel != 'COMPANY':
        razoes.append('a página é de MARCA/PRODUTO, não da empresa no país '
                      '(PAGE_ROLE=%s). O lote é COMPANY x COUNTRY: somar marca e '
                      'empresa faria a contagem por concorrente medir duas coisas '
                      'no mesmo balde.' % papel)
    apta = 'YES' if not razoes else 'NO'
    return {
        'ACCOUNT_CELL_ID': '%s|%s|%s' % (empresa, pais, plataforma),
        'COMPANY': empresa,
        'COUNTRY': pais,
        'PLATFORM': plataforma,
        'ACCOUNT_URL': url,
        'ACCOUNT_HANDLE': handle or NAO_SEI,
        'ACCOUNT_LABEL_ON_SITE': link.get('LABEL') or NAO_SEI,
        'ACCOUNT_IDENTITY_STATE': estado,
        'ACCOUNT_IDENTITY_EVIDENCE': ev,
        'COUNTRY_SCOPE': escopo_,
        'COUNTRY_SCOPE_EVIDENCE': ev_escopo,
        'PAGE_ROLE': papel,
        'PAGE_ROLE_EVIDENCE': ev_papel or (
            'nada na leitura indicou página de marca ou de produto; o padrão é a '
            'conta da própria empresa'),
        'ELIGIBLE_FOR_COMPANY_LOCAL_BATCH': apta,
        'EXCLUSION_REASONS': razoes,
        'COLLECTION_AUTHORIZED': apta,
        'COLLECTION_AUTHORIZED_WHY': (
            'PROVED + LOCAL_COUNTRY_PROVED + PAGE_ROLE=COMPANY — as três fecham'
            if apta == 'YES' else ' · '.join(razoes)),
    }


# ── PROVA DE IDA E VOLTA ────────────────────────────────────────────────────────
# O §0 aceita DOIS caminhos: site -> conta, e conta -> site. O primeiro é automático (o
# rodapé do âncora). O segundo exige abrir a conta e ler o que ELA declara — e isso foi
# feito à mão, no navegador, uma conta por vez. Esta tabela é FECHADA e auditável linha a
# linha, com a cadeia de URLs realmente lida escrita junto. Não é um mapa aberto: um mapa
# aberto voltaria a ser inferência, que é o que a missão inteira existe para evitar.
#
# Onde a volta NÃO fechou, não há linha aqui. Silêncio é NOT_KNOWN, não é reprovação.
PROVA_INVERSA = {
    # ── FECHARAM COMO LOCAL ────────────────────────────────────────────────────
    ('BAYER', 'FR', 'YOUTUBE', 'BayerAgri'): {
        'SCOPE': 'LOCAL_COUNTRY_PROVED',
        'CHAIN': ['https://www.youtube.com/@BayerAgri'],
        'EVIDENCE': (
            'a descrição do PRÓPRIO canal declara o país: "En France, à vos côtés, pour '
            'trouver des solutions adaptées à l\'agriculture française". Não é a língua '
            'do vídeo nem a língua da interface — é o canal dizendo a quem serve.'),
    },
    ('SYNGENTA', 'IT', 'FACEBOOK', 'Syngenta-2007689772789481'): {
        'SCOPE': 'LOCAL_COUNTRY_PROVED',
        'CHAIN': ['https://www.facebook.com/Syngenta-2007689772789481',
                  'https://www.syngenta.it/'],
        'EVIDENCE': (
            'ida e volta fechada. O identificador é um número de página e não dizia '
            'nada; a própria página declara o nome de usuário "syngentaitalia" e o site '
            '"syngenta.it", que é exatamente o âncora italiano.'),
    },
    ('BASF', 'IT', 'FACEBOOK', 'BASF-Agricultural-Solutions-1741459832625091'): {
        'SCOPE': 'LOCAL_COUNTRY_PROVED',
        'CHAIN': ['https://www.facebook.com/BASF-Agricultural-Solutions-1741459832625091/',
                  'https://www.agro.basf.it/it'],
        # POSTAL_ADDRESS_IN_COUNTRY = STRONG_COUNTRY_EVIDENCE. Nada além disso.
        #
        # A primeira redação dizia que endereço postal era "a evidência de país mais
        # forte que uma página pública dá". Isso é um RANKING, e nenhum ranking foi
        # medido nesta casa: não sabemos se endereço vale mais que domínio local, que
        # descrição explícita, que telefone ou que link do site oficial. Afirmar uma
        # ordem sem medir cria uma régua que outras missões vão herdar como se fosse
        # fato — e ranking herdado sem medição é como número que entra por parecer alto.
        'EVIDENCE': (
            'a página declara ENDEREÇO FÍSICO na Itália (Via Marconato 8, Cesano '
            'Maderno, Italy), telefone +39, e-mail info.agroitalia@basf.com e o site '
            'agro.basf.it/it, que é o âncora italiano. Quatro declarações de país '
            'independentes na mesma página. POSTAL_ADDRESS_IN_COUNTRY = '
            'STRONG_COUNTRY_EVIDENCE — sem ordenar contra as outras formas de prova, '
            'que esta missão não mediu.'),
    },

    # ── FECHARAM COMO NÃO-LOCAL. Também é resultado: tira a conta do limbo. ─────
    ('BASF', 'ES', 'LINKEDIN', 'basf'): {
        'SCOPE': 'GLOBAL',
        'CHAIN': ['https://www.linkedin.com/company/basf/'],
        'EVIDENCE': (
            'a própria página declara sede em Ludwigshafen, site basf.com e '
            '"mais de 111.000 funcionários (...) em quase todos os países do mundo". '
            'É a conta do grupo, não a da Espanha.'),
    },
    ('BASF', 'IT', 'LINKEDIN', 'basf'): {
        'SCOPE': 'GLOBAL',
        'CHAIN': ['https://www.linkedin.com/company/basf/'],
        'EVIDENCE': (
            'mesma conta do caso espanhol — sede Ludwigshafen, site basf.com, alcance '
            'mundial declarado. O `?originalSubdomain=it` da URL é preferência de '
            'exibição, não outra conta.'),
    },
    ('BAYER', 'IT', 'LINKEDIN', 'bayer-cropscience'): {
        'SCOPE': 'GLOBAL',
        'CHAIN': ['https://it.linkedin.com/company/bayer-cropscience'],
        'EVIDENCE': (
            'a página se chama "Bayer | Crop Science" e se descreve como "a responsible, '
            'GLOBAL team", sem país. E a prova de que o subdomínio é interface veio '
            'sozinha: pedir `it.linkedin.com` entregou a página em `de.linkedin.com`. '
            'Se `it.` fosse a Itália, `de.` seria a Alemanha — e é a MESMA conta.'),
    },
    # O CASO QUE OBRIGOU A SEPARAR PAÍS DE PAPEL. A localidade da DEKALB France está
    # PROVADA — a página se chama assim e aponta para o domínio francês da Bayer. Chamá-la
    # de "não local" era falso. O que a exclui é o PAPEL, e agora os dois convivem.
    ('BAYER', 'FR', 'FACEBOOK', 'dekalbfr'): {
        'SCOPE': 'LOCAL_COUNTRY_PROVED',
        'ROLE': 'PRODUCT_BRAND',
        'CHAIN': ['https://www.facebook.com/dekalbfr'],
        'EVIDENCE': (
            'o país está PROVADO: a página se chama "DEKALB France" e declara o site '
            'bayer-agri.fr, domínio agrícola francês da Bayer.'),
        'ROLE_EVIDENCE': (
            'a própria página se classifica como "Produto/serviço", e DEKALB é marca de '
            'SEMENTE da Bayer, não a conta da Bayer na França. Papel de marca não '
            'apaga a prova de país — as duas coisas são verdade ao mesmo tempo.'),
    },
    # Aqui as DUAS reprovam, e as duas ficam escritas. Colapsar em "PRODUCT" esconderia
    # que o país também não foi provado.
    ('CORTEVA', 'FR', 'YOUTUBE', 'CortevaBiologicals'): {
        'SCOPE': NAO_SEI,
        'ROLE': 'PRODUCT_BRAND',
        'CHAIN': ['https://www.youtube.com/@CortevaBiologicals'],
        'EVIDENCE': (
            'a descrição não nomeia país nenhum: "Stoller and Symborg became part of '
            'Corteva Biologicals". O site francês da Corteva lista o canal, mas o site '
            'onde o link aparece não prova o país da conta.'),
        'ROLE_EVIDENCE': (
            'o nome declarado é uma linha de negócio — Corteva Biologicals — e não a '
            'Corteva na França.'),
    },
    ('CORTEVA', 'FR', 'INSTAGRAM', 'cortevabiologicals'): {
        'SCOPE': NAO_SEI,
        'ROLE': 'PRODUCT_BRAND',
        'CHAIN': ['https://www.instagram.com/cortevabiologicals/'],
        'EVIDENCE': (
            'nome "Corteva Biologicals", bio "Growing Together" — nenhuma menção à '
            'França. Mesmo caso do canal de YouTube.'),
        'ROLE_EVIDENCE': 'linha de produto, não a empresa no país.',
    },

    ('BASF', 'ES', 'INSTAGRAM', 'basf_agroes'): {
        'SCOPE': 'LOCAL_COUNTRY_PROVED',
        'CHAIN': ['https://www.instagram.com/basf_agroes/',
                  'https://linktr.ee/basf_agroes',
                  'https://www.agro.basf.es/es/'],
        'EVIDENCE': (
            'ida e volta fechada. O site espanhol declara a conta, e a conta declara de '
            'volta o site espanhol: a bio do Instagram aponta para linktr.ee/basf_agroes, '
            'e essa página lista quatro endereços em agro.basf.es — incluindo a raiz '
            '/es/, que é exatamente o âncora. Não é a LÍNGUA da bio que decide (isso o §6 '
            'proíbe); é o endereço declarado.'),
    },
}


def promover_por_prova_inversa(contas):
    """Aplica a tabela fechada de ida-e-volta. Altera in-place."""
    for c in contas:
        chave = (c['COMPANY'], c['COUNTRY'], c['PLATFORM'], c.get('ACCOUNT_HANDLE'))
        p = PROVA_INVERSA.get(chave)
        if not p or c['ACCOUNT_IDENTITY_STATE'] != 'PROVED':
            continue
        c['COUNTRY_SCOPE'] = p['SCOPE']
        c['COUNTRY_SCOPE_EVIDENCE'] = p['EVIDENCE']
        c['COUNTRY_SCOPE_CHAIN'] = p['CHAIN']
        if p.get('ROLE'):
            c['PAGE_ROLE'] = p['ROLE']
            c['PAGE_ROLE_EVIDENCE'] = p.get('ROLE_EVIDENCE') or NAO_SEI
        _reavaliar(c)


def _reavaliar(c):
    """Recalcula elegibilidade a partir das TRÊS perguntas. Altera in-place.

    Existe para que a regra viva num lugar só. Antes ela estava escrita em `_linha` e
    repetida em cada promotor — e regra copiada é regra que diverge na primeira pressa.
    """
    razoes = []
    if c['ACCOUNT_IDENTITY_STATE'] != 'PROVED':
        razoes.append('a conta não está PROVED como oficial (%s)'
                      % c['ACCOUNT_IDENTITY_STATE'])
    if c.get('COUNTRY_SCOPE') != 'LOCAL_COUNTRY_PROVED':
        razoes.append('o país da conta não está provado como %s (COUNTRY_SCOPE=%s)'
                      % (c['COUNTRY'], c.get('COUNTRY_SCOPE')))
    if c.get('PAGE_ROLE') != 'COMPANY':
        razoes.append('a página é de MARCA/PRODUTO, não da empresa no país '
                      '(PAGE_ROLE=%s). O lote é COMPANY x COUNTRY.' % c.get('PAGE_ROLE'))
    apta = 'YES' if not razoes else 'NO'
    c['ELIGIBLE_FOR_COMPANY_LOCAL_BATCH'] = apta
    c['EXCLUSION_REASONS'] = razoes
    c['COLLECTION_AUTHORIZED'] = apta
    c['COLLECTION_AUTHORIZED_WHY'] = (
        'PROVED + LOCAL_COUNTRY_PROVED + PAGE_ROLE=COMPANY — as três fecham'
        if apta == 'YES' else ' · '.join(razoes))


def _achatado(handle):
    return re.sub(r'[^a-z0-9]+', '', urllib.parse.unquote(handle or '').lower())


def promover_por_irmao(contas):
    """O MESMO handle em outra plataforma, já LOCAL, promove o escopo. Altera in-place.

    Nasce de um caso real e de uma injustiça do alfabeto: o site espanhol da Bayer
    declara `facebook.com/Bayer4CropsES` e `instagram.com/bayer4cropses`. É o MESMO
    identificador; só a caixa muda, porque cada plataforma escreve URL do seu jeito. A
    régua de escopo lê "ES" como palavra no primeiro e não lê nada no segundo — e a
    mesma conta sairia LOCAL no Facebook e NOT_KNOWN no Instagram.

        CAIXA DA URL != ESCOPO DA CONTA.

    A promoção exige identidade EXATA depois de tirar caixa e pontuação, e exige que o
    irmão já seja LOCAL_COUNTRY por evidência própria. Não é semelhança: `basf_agroes`
    e `basf.agro.espana` NÃO se promovem, porque não são o mesmo identificador — são
    duas contas diferentes da mesma empresa, e adivinhar isso seria o erro de sempre.
    """
    locais = {_achatado(c['ACCOUNT_HANDLE']): c for c in contas
              if c.get('COUNTRY_SCOPE') == 'LOCAL_COUNTRY_PROVED'}
    for c in contas:
        if c.get('COUNTRY_SCOPE') != NAO_SEI or c['ACCOUNT_IDENTITY_STATE'] != 'PROVED':
            continue
        irmao = locais.get(_achatado(c['ACCOUNT_HANDLE']))
        if not irmao or irmao is c:
            continue
        # O irmão promove o PAÍS. Ele NÃO promove o papel: a página pode ser da marca e
        # do país ao mesmo tempo, e quem decide papel é a leitura da própria página.
        c['COUNTRY_SCOPE'] = 'LOCAL_COUNTRY_PROVED'
        c['COUNTRY_SCOPE_EVIDENCE'] = (
            'o mesmo identificador ("%s") aparece no %s da mesma empresa e país, onde '
            'ele carrega marca de país explícita. Mesma conta, caixa diferente porque a '
            'plataforma escreve a URL do seu jeito.'
            % (c['ACCOUNT_HANDLE'], irmao['PLATFORM']))
        _reavaliar(c)


def montar(caminho=EVIDENCIA):
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)

    contas, silencio = [], []
    for a in d['ANCHORS']:
        resolvidas = resolver(a)
        promover_por_prova_inversa(resolvidas)
        promover_por_irmao(resolvidas)
        contas.extend(resolvidas)
        achadas = {c['PLATFORM'] for c in resolvidas
                   if c['ACCOUNT_IDENTITY_STATE'] != 'REJECTED'}
        for plataforma in ('LINKEDIN', 'YOUTUBE', 'INSTAGRAM', 'FACEBOOK'):
            if plataforma not in achadas:
                silencio.append({
                    'ACCOUNT_CELL_ID': '%s|%s|%s' % (a['COMPANY'], a['COUNTRY'], plataforma),
                    'COMPANY': a['COMPANY'], 'COUNTRY': a['COUNTRY'],
                    'PLATFORM': plataforma,
                    'ACCOUNT_IDENTITY_STATE': NAO_SEI,
                    'ACCOUNT_IDENTITY_EVIDENCE': (
                        'o site oficial local (%s) NÃO declara link para esta '
                        'plataforma. Isto é ausência de DECLARAÇÃO, nunca ausência '
                        'de conta nem ausência de comunicação.' % a['FINAL_URL']),
                    'COLLECTION_AUTHORIZED': 'NO',
                })

    por_estado, por_escopo, por_papel = {}, {}, {}
    for c in contas:
        e = c['ACCOUNT_IDENTITY_STATE']
        por_estado[e] = por_estado.get(e, 0) + 1
        if e != 'REJECTED':
            s = c.get('COUNTRY_SCOPE', NAO_SEI)
            por_escopo[s] = por_escopo.get(s, 0) + 1
            r = c.get('PAGE_ROLE', NAO_SEI)
            por_papel[r] = por_papel.get(r, 0) + 1
    por_estado[NAO_SEI] = por_estado.get(NAO_SEI, 0) + len(silencio)

    # A exclusão é contada por UM motivo primário, senão a soma passa do total. A ordem
    # é papel primeiro: uma página de marca fica fora do lote COMPANY x COUNTRY mesmo com
    # o país provado, então o papel é o motivo que decide sozinho. Os outros motivos
    # continuam inteiros em EXCLUSION_REASONS de cada linha — nada se perde.
    fora_por_motivo = {}
    for c in contas:
        if c['ACCOUNT_IDENTITY_STATE'] != 'PROVED' or c['COLLECTION_AUTHORIZED'] == 'YES':
            continue
        if c.get('PAGE_ROLE') != 'COMPANY':
            k = 'PRODUCT_BRAND_ROLE'
        elif c.get('COUNTRY_SCOPE') in ('GLOBAL', 'REGIONAL_EUROPE', 'OTHER'):
            k = c['COUNTRY_SCOPE']
        else:
            k = 'COUNTRY_NOT_KNOWN'
        fora_por_motivo[k] = fora_por_motivo.get(k, 0) + 1

    autorizadas = [c for c in contas if c['COLLECTION_AUTHORIZED'] == 'YES']
    return {
        'SOURCE_ID': 'COMPETITOR-PUBLIC-COMM/CONTAS-V1',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'derivado de ANCORAS-EVIDENCIA-V1 — nenhuma coleta, nenhuma busca',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'n/a',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_IDENTITY',
        'APIFY_RUNS': 0,
        'COST_USD': 0,
        'REGRA_DE_PROMOCAO': (
            'TRÊS perguntas independentes: a conta é OFICIAL? é DAQUELE PAÍS? é da '
            'EMPRESA ou de uma MARCA? '
            'ELIGIBLE_FOR_COMPANY_LOCAL_BATCH = PROVED E LOCAL_COUNTRY_PROVED E '
            'PAGE_ROLE=COMPANY.'),
        'OS_QUATRO_ESTADOS_SAO_DIFERENTES': {
            'LOCAL_COUNTRY_PROVED': 'o país da conta está provado por evidência declarada',
            'GLOBAL': 'a conta declara alcance mundial ou sede fora do país',
            'PRODUCT_BRAND (PAGE_ROLE)': (
                'a página é de uma marca/produto. NÃO é um estado de país: uma página '
                'de marca pode ter o país PROVADO — a DEKALB France tem — e mesmo assim '
                'ficar fora do lote COMPANY x COUNTRY.'),
            'NOT_KNOWN': 'não foi possível decidir por rota pública. Não é reprovação.',
        },
        'ACCOUNTS_ATTEMPTED': len(contas) + len(silencio),
        'ACCOUNTS_FOUND_AS_LINK': len(contas),
        'BY_IDENTITY_STATE': por_estado,
        'BY_COUNTRY_SCOPE': por_escopo,
        'BY_PAGE_ROLE': por_papel,
        'EXCLUDED_BY_PRIMARY_REASON': fora_por_motivo,
        'ACCOUNTS_AUTHORIZED_FOR_COLLECTION': len(autorizadas),
        'ACCOUNTS': contas,
        'NO_LINK_DECLARED': silencio,
    }


if __name__ == '__main__':
    corpo = montar()
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'CONTAS-V1.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('casas tentadas (empresa x país x plataforma): %d'
          % corpo['ACCOUNTS_ATTEMPTED'])
    print('links encontrados nos sites oficiais:          %d'
          % corpo['ACCOUNTS_FOUND_AS_LINK'])
    print('por estado:   %s' % corpo['BY_IDENTITY_STATE'])
    print('por país:     %s' % corpo['BY_COUNTRY_SCOPE'])
    print('por papel:    %s' % corpo['BY_PAGE_ROLE'])
    print('excluídas:    %s' % corpo['EXCLUDED_BY_PRIMARY_REASON'])
    print('')
    print('AUTORIZADAS A COLETAR: %d' % corpo['ACCOUNTS_AUTHORIZED_FOR_COLLECTION'])
    for c in corpo['ACCOUNTS']:
        if c['COLLECTION_AUTHORIZED'] == 'YES':
            print('  %-9s %s  %-10s %s' % (c['COMPANY'], c['COUNTRY'],
                                           c['PLATFORM'], c['ACCOUNT_URL']))
    print('')
    print('OFICIAIS FORA DO LOTE COMPANY x COUNTRY — país e papel em colunas separadas:')
    print('  %-9s %-3s %-10s %-22s %-14s %s'
          % ('EMPRESA', 'PAÍS', 'PLATAFORMA', 'COUNTRY_SCOPE', 'PAGE_ROLE', 'HANDLE'))
    for c in corpo['ACCOUNTS']:
        if c['ACCOUNT_IDENTITY_STATE'] == 'PROVED' and c['COLLECTION_AUTHORIZED'] == 'NO':
            print('  %-9s %-3s %-10s %-22s %-14s %s'
                  % (c['COMPANY'], c['COUNTRY'], c['PLATFORM'],
                     c['COUNTRY_SCOPE'], c['PAGE_ROLE'], c['ACCOUNT_HANDLE']))
