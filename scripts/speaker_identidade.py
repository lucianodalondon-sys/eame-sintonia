#!/usr/bin/env python3
"""
IDENTIDADE DO SPEAKER — o portão que roda ANTES de qualquer execução paga.

    python3 scripts/speaker_identidade.py montar
    python3 scripts/speaker_identidade.py resumo

O QUE ESTE ARQUIVO DECIDE, E POR QUE ELE VEM ANTES DA COLETA
--------------------------------------------------------------
O piloto EARLY SIGNAL é **identity-first**. A pergunta não é "quem tem alcance", é "quem
tem âncora técnica verificável". Sem âncora, o conteúdo coletado não tem a quem ser
atribuído — e atribuir conteúdo à pessoa errada é o erro mais caro já medido nesta casa:

    a busca por "Pasquale De Vita" no LinkedIn devolveu o presidente da Unione
    Petrolifera, um vendedor de esquadrias e um diretor de TI, todos de nome idêntico.
    Um portão que parasse no nome teria promovido o presidente da associação do
    petróleo a pesquisador de trigo duro.

Por isso a lei aqui é `NAME_MATCH != PERSON`, e ela é executada, não escrita.

DUAS FORÇAS DE ORCID, E ELAS NÃO SÃO A MESMA COISA
----------------------------------------------------
O `RESEARCHER-OUTLOOK-V1` já separou os dois estados, e a separação continua valendo:

    ORCID_DECLARED     o registro de autor do OpenAlex traz um ORCID. Isso é o OpenAlex
                       afirmando. Não foi conferido com a fonte.
    ORCID_RESOLVED     o registro ORCID foi BUSCADO na fonte, respondeu, e o sobrenome
                       bate. Agora existem duas fontes independentes dizendo o mesmo.

Um ORCID que o OpenAlex declara e a fonte não resolve não é identidade — é um ponteiro
quebrado, e sai como tal.

O EMPREGADOR DECLARADO NO ORCID É EVIDÊNCIA SEPARADA, E ÀS VEZES DISCORDA
--------------------------------------------------------------------------
Medido na primeira sonda: para `0000-0003-1895-5895`, o OpenAlex diz *Instituto de
Agricultura Sostenible* e o ORCID diz *Estación Experimental del Zaidín*. As duas são
CSIC, e a divergência é informação — mudança de lotação, afiliação múltipla, ou registro
desatualizado de um dos lados. **Ela é registrada, nunca reconciliada em silêncio**, e
`INSTITUTION_AGREEMENT` publica qual dos três casos ocorreu.

O TRAVESSÃO QUE QUEBRARIA A COMPARAÇÃO
----------------------------------------
O OpenAlex escreve `Jesús Mercado‐Blanco` com HÍFEN U+2010; o ORCID escreve
`Mercado-Blanco` com hífen ASCII. Comparar as duas strings cruas devolve "não bate" para
a mesma pessoa. Este é o bug de acento que o handoff lista como reincidente — aqui ele é
tratado em `_chave()`, com o travessão, o acento e a caixa normalizados **antes** de
qualquer comparação.

O GUARDA DE CONFLAÇÃO — herdado, porque já pegou um caso real
---------------------------------------------------------------
`Nikolaos Papadopoulos` estava em primeira posição no quadro espanhol com **58
organizações declaradas contra mediana 2**. Não era um pesquisador prolífico: era um id
do OpenAlex que juntou homônimos. O teto aqui é **derivado da mediana do próprio quadro**
(10x), nunca escolhido a dedo, para que ele acompanhe o quadro em vez de virar um número
mágico.

    CONTAGEM ALTA NÃO VALIDA IDENTIDADE.

O QUE ESTE ARQUIVO NÃO FAZ
---------------------------
Não procura canal público, não coleta post, não chama Apify, não ordena por seguidores e
não cria score de autoridade. `FOLLOWERS != AUTHORITY` continua sendo lei.
"""
import json
import os
import sys
import time
import unicodedata
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
RAWDIR = os.path.join(ROOT, 'data', 'raw', 'SPEAKER-UNIVERSO')
CACHE = os.path.join(RAWDIR, 'orcid')
DEST = os.path.join(SAMPLES, 'SPEAKER-UNIVERSE-PILOT-V1.json')

ORCID_API = 'https://pub.orcid.org/v3.0/%s/%s'
PAUSA = 0.7

NAO_SEI = 'NÃO SEI'

# OS SEIS RECORTES CONGELADOS PELO ÁRBITRO, e a chave de scope que os localiza no universo
# montado por `speaker_universo.py`. A ordem manda: RECORTE -> IDENTIDADE -> CANAL ->
# CONTEÚDO. Nunca pessoa primeiro e assunto depois.
CASOS = [
    ('ES-OLIVE-REPILO', 'ES', 'OLIVE', 'REPILO', 'OLIVE|REPILO'),
    ('ES-CEREAL-SEPTORIA', 'ES', 'CEREAL', 'SEPTORIA', 'CEREAL|SEPTORIA'),
    ('IT-VINE-FLAVESCENCE', 'IT', 'VINE', 'FLAVESCENCE', 'VINE|FLAVESCENCE'),
    ('IT-DURUM_WHEAT-FUSARIUM', 'IT', 'DURUM_WHEAT', 'FUSARIUM', 'DURUM_WHEAT|FUSARIUM'),
    ('FR-VINE-DOWNY_MILDEW', 'FR', 'VINE', 'DOWNY_MILDEW', 'VINE|DOWNY_MILDEW'),
    ('FR-CEREAL-SEPTORIA', 'FR', 'CEREAL', 'SEPTORIA', 'CEREAL|SEPTORIA'),
]

# PRIMEIRO CHECKPOINT. O árbitro mandou parar em ~10 identidades PROVADAS, distribuídas
# entre os seis, sem forçar igualdade. Duas tentativas por recorte dão 12 tentadas para
# ~10 provadas — e se sobrar folga, ela é declarada, não preenchida.
POR_CASO_NO_CHECKPOINT = 2
META_PROVADAS = 10

ANO_MINIMO = 2024      # "fala hoje" — obra em 2019 e silêncio desde 2022 não é sensor


# ------------------------------------------------------------------ normalização de nome
def _chave(s):
    """Nome comparável: sem acento, sem travessão exótico, sem caixa, sem pontuação.

    O travessão U+2010 do OpenAlex contra o hífen ASCII do ORCID faria a MESMA pessoa
    sair como divergente. Normalizar antes de comparar é o que impede isso.
    """
    if not s:
        return ''
    s = unicodedata.normalize('NFKD', str(s))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    for tracinho in ('‐', '‑', '‒', '–', '—', '−'):
        s = s.replace(tracinho, '-')
    s = s.replace('-', ' ').replace('.', ' ').replace(',', ' ').replace("'", ' ')
    return ' '.join(s.lower().split())


def _sobrenome(nome):
    """Último token com 2+ letras. Suficiente para o teste, e honesto sobre o que é."""
    ts = [t for t in _chave(nome).split() if len(t) > 1]
    return ts[-1] if ts else ''


def _id_orcid(v):
    """Aceita '0000-...' ou 'https://orcid.org/0000-...'. Devolve só o id, ou ''."""
    if not v:
        return ''
    return str(v).rstrip('/').split('/')[-1].strip()


# ------------------------------------------------------------------------ fonte ORCID
def _buscar(orcid, secao):
    """Uma seção do registro ORCID, com cache em disco. NUNCA levanta."""
    os.makedirs(CACHE, exist_ok=True)
    caminho = os.path.join(CACHE, '%s.%s.json' % (orcid, secao))
    if os.path.exists(caminho):
        try:
            with open(caminho, encoding='utf-8') as f:
                return json.load(f), None
        except ValueError:
            pass
    req = urllib.request.Request(ORCID_API % (orcid, secao),
                                 headers={'Accept': 'application/json',
                                          'User-Agent': 'SintoniaEAME'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return None, 'HTTP %d' % e.code
    except Exception as e:                                   # noqa: BLE001
        return None, type(e).__name__
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False)
    time.sleep(PAUSA)
    return d, None


# ------------------------------------------------------------------ canais declarados
# Host -> plataforma. O ORCID tem um campo `researcher-urls` onde a PRÓPRIA pessoa declara
# seus endereços públicos. É a fonte mais barata e mais defensável de canal que existe
# aqui: não é busca por nome, não é scraping, não é inferência — é declaração.
#
#     NAME != HANDLE != URL continua valendo. A diferença é que aqui quem ligou o nome à
#     URL foi o dono do nome.
HOSTS = [
    ('linkedin.com', 'LINKEDIN'),
    ('youtube.com', 'YOUTUBE'), ('youtu.be', 'YOUTUBE'),
    ('instagram.com', 'INSTAGRAM'),
    ('twitter.com', 'TWITTER_X'), ('x.com', 'TWITTER_X'),
    ('researchgate.net', 'RESEARCHGATE'),
    ('scholar.google', 'GOOGLE_SCHOLAR'),
]


def canais_declarados(oid):
    """→ (dicionário plataforma->url, lista crua). Só o que o ORCID declara."""
    if not oid:
        return {}, []
    d, err = _buscar(oid, 'person')
    if err or not d:
        return {}, []
    achados, crus = {}, []
    for u in ((d.get('researcher-urls') or {}).get('researcher-url') or []):
        url = ((u.get('url') or {}).get('value') or '').strip()
        if not url:
            continue
        crus.append({'NAME': u.get('url-name'), 'URL': url})
        alvo = url.lower()
        plat = next((p for h, p in HOSTS if h in alvo), None)
        if not plat:
            # Página institucional é canal público de verdade — o piloto aceita
            # explicitamente vídeo institucional, webinar e gravação de congresso.
            plat = 'INSTITUTIONAL_OR_PERSONAL'
        achados.setdefault(plat, []).append(url)
    return achados, crus


def verificar(orcid, nome_openalex, inst_openalex, pais_do_recorte=None):
    """→ dicionário de identidade. Estado derivado do que a fonte devolveu, não afirmado."""
    oid = _id_orcid(orcid)
    fora = {
        'ORCID': oid or NAO_SEI,
        'ORCID_STATE': 'ORCID_ABSENT',
        'ORCID_NAME': NAO_SEI,
        'ORCID_EMPLOYER': NAO_SEI,
        'ORCID_EMPLOYER_CURRENT': NAO_SEI,
        'ORCID_EMPLOYER_COUNTRY': NAO_SEI,
        'ORCID_DECLARED_ROLE': NAO_SEI,
        'ORCID_ORG_ID': NAO_SEI,
        'NAME_AGREEMENT': NAO_SEI,
        'INSTITUTION_AGREEMENT': NAO_SEI,
        'COUNTRY_AGREEMENT': NAO_SEI,
        'IDENTITY_STATE': 'IDENTITY_NOT_PROVED',
        'IDENTITY_EVIDENCE': 'sem ORCID no registro de autor do OpenAlex',
    }
    if not oid:
        return fora

    pessoa, err = _buscar(oid, 'person')
    if err:
        fora['ORCID_STATE'] = 'ORCID_NOT_RESOLVED'
        fora['IDENTITY_EVIDENCE'] = (
            'ORCID declarado pelo OpenAlex (%s) e a fonte pub.orcid.org respondeu %s. '
            'Ponteiro não resolvido não é identidade.' % (oid, err))
        return fora

    n = (pessoa.get('name') or {})
    dado = ' '.join(x for x in [
        ((n.get('given-names') or {}) or {}).get('value') or '',
        ((n.get('family-name') or {}) or {}).get('value') or ''] if x).strip()
    fora['ORCID_STATE'] = 'ORCID_RESOLVED'
    fora['ORCID_NAME'] = dado or NAO_SEI

    bate = bool(dado) and _sobrenome(dado) == _sobrenome(nome_openalex)
    fora['NAME_AGREEMENT'] = 'FAMILY_NAME_MATCH' if bate else 'FAMILY_NAME_DIVERGES'

    emps, err2 = _buscar(oid, 'employments')
    atuais, todos = [], []
    if not err2:
        for g in (emps or {}).get('affiliation-group', []):
            for s in g.get('summaries', []):
                e = s.get('employment-summary') or {}
                o = e.get('organization') or {}
                org = (o.get('name') or '').strip()
                if not org:
                    continue
                d_ = o.get('disambiguated-organization') or {}
                reg = {
                    'ORG': org,
                    'COUNTRY': ((o.get('address') or {}).get('country') or '').upper(),
                    'ROLE': (e.get('role-title') or '').strip(),
                    'ORG_ID': ('%s:%s' % (d_.get('disambiguation-source'),
                                          d_.get('disambiguated-organization-identifier'))
                               if d_.get('disambiguated-organization-identifier') else ''),
                    'CURRENT': e.get('end-date') is None,
                }
                todos.append(reg)
                if reg['CURRENT']:
                    atuais.append(reg)

    # O emprego ATUAL manda. Sem emprego atual, o mais recente que a fonte listou.
    principal = (atuais or todos or [None])[0]
    if principal:
        fora['ORCID_EMPLOYER'] = principal['ORG']
        fora['ORCID_EMPLOYER_COUNTRY'] = principal['COUNTRY'] or NAO_SEI
        fora['ORCID_DECLARED_ROLE'] = principal['ROLE'] or NAO_SEI
        fora['ORCID_ORG_ID'] = principal['ORG_ID'] or NAO_SEI
    fora['ORCID_EMPLOYER_CURRENT'] = atuais[0]['ORG'] if atuais else NAO_SEI

    if not todos:
        fora['INSTITUTION_AGREEMENT'] = 'ORCID_DECLARES_NO_EMPLOYER'
    else:
        alvo = _chave(inst_openalex)
        casou = any(_chave(r['ORG']) == alvo or _chave(r['ORG']) in alvo
                    or alvo in _chave(r['ORG']) for r in todos if alvo)
        fora['INSTITUTION_AGREEMENT'] = 'AGREES' if casou else 'DIVERGES'

    # O TESTE QUE FALTAVA, E QUE UMA PESSOA REAL REPROVOU.
    # A primeira versão dava IDENTITY_PROVED só com sobrenome batendo. Com isso, Lukas
    # Meile entrou como ES — porque o OpenAlex registrou afiliação espanhola numa obra —
    # enquanto o empregador que ele mesmo declara no ORCID é a ETH Zurich, na Suíça.
    # Coletar a "voz espanhola de septoriose" nessa pessoa poria país errado no registro.
    # Agora o país do recorte tem de bater com o país que o ORCID declara.
    paises = {r['COUNTRY'] for r in todos if r['COUNTRY']}
    paises_atuais = {r['COUNTRY'] for r in atuais if r['COUNTRY']}
    if not pais_do_recorte:
        fora['COUNTRY_AGREEMENT'] = 'NOT_TESTED'
    elif not paises:
        fora['COUNTRY_AGREEMENT'] = 'ORCID_DECLARES_NO_COUNTRY'
    elif pais_do_recorte in (paises_atuais or paises):
        fora['COUNTRY_AGREEMENT'] = 'AGREES'
    elif pais_do_recorte in paises:
        fora['COUNTRY_AGREEMENT'] = 'AGREES_IN_PAST_ONLY'
    else:
        fora['COUNTRY_AGREEMENT'] = 'DIVERGES'

    if not bate:
        fora['IDENTITY_STATE'] = 'IDENTITY_PARTIAL'
        fora['IDENTITY_EVIDENCE'] = (
            'ORCID %s resolve, mas o sobrenome do ORCID ("%s") não bate com o do OpenAlex '
            '("%s"). Divergência registrada, não reconciliada.' % (oid, dado, nome_openalex))
    elif fora['COUNTRY_AGREEMENT'] == 'DIVERGES':
        fora['IDENTITY_STATE'] = 'IDENTITY_PARTIAL_COUNTRY_DIVERGES'
        fora['IDENTITY_EVIDENCE'] = (
            'ORCID %s resolve e o sobrenome bate, MAS o país do empregador declarado no '
            'ORCID é %s e o recorte é %s. A afiliação %s veio de UMA obra no OpenAlex; o '
            'ORCID diz outra coisa sobre onde a pessoa trabalha. Não promovo: pessoa em '
            'país errado contamina COUNTRY_OF_PERSON.'
            % (oid, ','.join(sorted(paises)), pais_do_recorte, inst_openalex))
    elif fora['COUNTRY_AGREEMENT'] == 'AGREES_IN_PAST_ONLY':
        # Medido em Lukas Meile: CBGP Madrid (ES) com `end-date` preenchido, e ETH Zurich
        # (CH) como emprego ATUAL. O OpenAlex o trouxe pelo recorte espanhol porque UMA
        # obra carrega a afiliação de Madri. Promovê-lo poria um pesquisador hoje suíço
        # dentro da voz técnica espanhola de septoriose.
        #
        #     PAST_AFFILIATION != CURRENT_COUNTRY.
        fora['IDENTITY_STATE'] = 'IDENTITY_PARTIAL_COUNTRY_PAST'
        fora['IDENTITY_EVIDENCE'] = (
            'ORCID %s resolve e o sobrenome bate. O vínculo com %s existiu e ESTÁ '
            'ENCERRADO no próprio ORCID (end-date preenchido); o emprego atual declarado '
            'é %s (%s). A pessoa é real e o par técnico é o certo — o país é que não é '
            'mais este.' % (oid, pais_do_recorte, fora['ORCID_EMPLOYER'],
                            fora['ORCID_EMPLOYER_COUNTRY']))
    elif fora['COUNTRY_AGREEMENT'] == 'ORCID_DECLARES_NO_COUNTRY':
        # O ORCID existe e resolve, mas a pessoa não declarou emprego nenhum lá. O país
        # então repousa SÓ no OpenAlex. É utilizável e é honesto dizer que é fonte única.
        fora['IDENTITY_STATE'] = 'IDENTITY_PROVED_COUNTRY_SINGLE_SOURCE'
        fora['IDENTITY_EVIDENCE'] = (
            'ORCID %s resolvido e sobrenome batendo ("%s" x "%s"), mas o registro ORCID '
            'não declara empregador. O país %s vem SÓ da afiliação do OpenAlex — fonte '
            'única, não duas fontes concordando.'
            % (oid, dado, nome_openalex, pais_do_recorte))
    else:
        fora['IDENTITY_STATE'] = 'IDENTITY_PROVED'
        fora['IDENTITY_EVIDENCE'] = (
            'ORCID %s resolvido em pub.orcid.org; sobrenome do ORCID ("%s") bate com o do '
            'OpenAlex ("%s"); empregador declarado no ORCID: %s (%s), papel declarado '
            '"%s", id de organização %s. Duas fontes independentes, não uma afirmação.'
            % (oid, dado, nome_openalex, fora['ORCID_EMPLOYER'],
               fora['ORCID_EMPLOYER_COUNTRY'], fora['ORCID_DECLARED_ROLE'],
               fora['ORCID_ORG_ID']))
    return fora


# ------------------------------------------------------------------------- candidatos
def _teto_conflacao(pessoas):
    """Teto de organizações DERIVADO da mediana do quadro — 10x, como no caso espanhol."""
    ns = sorted(p.get('ALL_INSTITUTIONS_COUNT') or 1 for p in pessoas)
    if not ns:
        return 20
    m = ns[len(ns) // 2]
    return max(10, m * 10)


def _fila_es_olive():
    """A fila espanhola que o repositório JÁ derivou. Só quem tem REPILO na âncora.

    A fila de 20 foi construída com âncora de olivar INTEIRA — nem todos os 20 têm repilo.
    Filtrar aqui é o que impede o recorte congelado de ser diluído por quem estuda
    verticillium ou xylella. É o mesmo par, ou não é o par.
    """
    with open(os.path.join(SAMPLES, 'RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json'),
              encoding='utf-8') as f:
        d = json.load(f)
    fora = []
    for p in d['QUEUE']:
        if 'REPILO' not in (p.get('ISSUE') or []):
            continue
        fora.append({
            'PERSON_ID': p['PERSON_ID'], 'NAME': p['NAME'], 'ORCID': p.get('ORCID'),
            'INSTITUTION': p.get('INSTITUTION') or NAO_SEI,
            'ALL_INSTITUTIONS_COUNT': p.get('ALL_INSTITUTIONS_COUNT'),
            'WORKS_IN_SCOPE': p.get('PUBLICATION_COUNT_IN_SCOPE'),
            'LAST_YEAR': p.get('LAST_KNOWN_ACTIVITY'),
            'CROPS': ['OLIVE'], 'ISSUES': ['REPILO'],
            'ORIGIN': 'RESEARCHER-PUBLIC-VOICE-QUEUE-ES (derivada por scripts/filas.py)',
        })
    return fora


def _do_universo(pais, scope_key):
    """Só quem entrou POR AQUELE recorte. A pessoa herda o crop×issue da consulta."""
    caminho = os.path.join(RAWDIR, 'universo-%s.json' % pais)
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    crop, issue = scope_key.split('|')
    fora = []
    for p in d['PEOPLE']:
        if scope_key not in p['SCOPES']:
            continue
        fora.append({
            'PERSON_ID': p['PERSON_ID'], 'NAME': p['NAME'], 'ORCID': p.get('ORCID'),
            'INSTITUTION': p.get('INSTITUTION') or NAO_SEI,
            'ALL_INSTITUTIONS_COUNT': p.get('ALL_INSTITUTIONS_COUNT'),
            'WORKS_IN_SCOPE': p.get('WORKS_IN_SCOPE'), 'LAST_YEAR': p.get('LAST_YEAR'),
            'CROPS': [crop], 'ISSUES': [issue],
            'ORIGIN': 'SPEAKER-UNIVERSO-%s (OpenAlex, rota gratuita)' % pais,
        })
    return fora


def candidatos(caso_id, pais, scope_key):
    """Candidatos DO RECORTE. Dedupe por PERSON_ID quando duas rotas trazem o mesmo."""
    fonte = _do_universo(pais, scope_key)
    if caso_id == 'ES-OLIVE-REPILO':
        fonte = _fila_es_olive() + fonte
    vistos, fora = set(), []
    for c in fonte:
        if c['PERSON_ID'] in vistos:
            continue
        vistos.add(c['PERSON_ID'])
        fora.append(c)
    return fora


def selecionar(cands, quantos):
    """Filtra por critérios declarados e devolve (selecionados, recusas, elegíveis, teto)."""
    teto = _teto_conflacao(cands)
    recusa, elegiveis = {}, []
    for c in cands:
        motivos = []
        if not _id_orcid(c.get('ORCID')):
            motivos.append('sem ORCID')
        if (c.get('INSTITUTION') or NAO_SEI) == NAO_SEI:
            motivos.append('sem instituição declarada')
        if (c.get('LAST_YEAR') or 0) < ANO_MINIMO:
            motivos.append('sem obra desde %d' % ANO_MINIMO)
        if (c.get('ALL_INSTITUTIONS_COUNT') or 1) > teto:
            motivos.append('possível conflação: %d organizações, teto derivado %d'
                           % (c.get('ALL_INSTITUTIONS_COUNT') or 0, teto))
        if motivos:
            for m in motivos:
                recusa[m.split(':')[0]] = recusa.get(m.split(':')[0], 0) + 1
            continue
        elegiveis.append(c)
    elegiveis.sort(key=lambda c: (-(c['WORKS_IN_SCOPE'] or 0), c['NAME'] or ''))
    return elegiveis[:quantos], recusa, len(elegiveis), teto


def montar(por_caso=POR_CASO_NO_CHECKPOINT):
    blocos, pessoas = {}, []
    for caso_id, pais, crop, issue, scope in CASOS:
        cands = candidatos(caso_id, pais, scope)
        # REGRA DE REPOSIÇÃO, declarada antes de rodar: tenta até obter `por_caso`
        # identidades provadas, com TETO de o dobro de tentativas. Candidato recusado pelo
        # portão de país é REPOSTO pelo próximo elegível — isso é o portão funcionando,
        # não o desenho sendo ajustado depois do resultado. O teto existe para a reposição
        # não virar uma busca até dar certo.
        sel, recusa, n_eleg, teto = selecionar(cands, por_caso * 2)
        usados, provadas = [], 0
        for c in sel:
            if provadas >= por_caso:
                break
            ident = verificar(c['ORCID'], c['NAME'], c['INSTITUTION'], pais)
            if ident['IDENTITY_STATE'].startswith('IDENTITY_PROVED'):
                provadas += 1
            usados.append((c, ident))
        sel = [c for c, _ in usados]
        for c, ident in usados:
            pessoas.append({
                'CASE_ID': caso_id,
                'PERSON_ID': c['PERSON_ID'],
                'NAME': c['NAME'],
                'ENTITY_KIND': 'PERSON',
                'COUNTRY': pais,
                'COUNTRY_BASIS': ('afiliação institucional declarada — NÃO é nacionalidade '
                                  'e NÃO foi inferida por idioma'),
                'INSTITUTION': c['INSTITUTION'],
                # SOURCE_ENTITY existe para medir independência DEPOIS: pesquisador do
                # IFAPA + vídeo do IFAPA não são duas fontes independentes.
                'SOURCE_ENTITY': c['INSTITUTION'],
                'ROLE': 'RESEARCHER',
                'ROLE_BASIS': ('afiliação institucional declarada em campo estruturado do '
                               'OpenAlex; nunca de prosa livre'),
                'TECHNICAL_DOMAIN': sorted(set(c['ISSUES'])),
                'CROPS': c['CROPS'],
                'ISSUES': c['ISSUES'],
                'WORKS_IN_SCOPE': c['WORKS_IN_SCOPE'],
                'LAST_KNOWN_ACTIVITY': c['LAST_YEAR'],
                'ORIGIN_OF_CANDIDATE': c['ORIGIN'],
                # Canal DECLARADO pelo próprio ORCID entra agora, de graça. O que ele não
                # declara fica NOT_TESTED — que é "não procurei", nunca "não tem". Buscar
                # LinkedIn/YouTube por nome é a etapa paga e ainda não foi feita.
                'PUBLIC_CHANNELS': dict(
                    {'LINKEDIN': 'NOT_TESTED', 'YOUTUBE': 'NOT_TESTED',
                     'INSTAGRAM': 'NOT_TESTED'},
                    **{k: v for k, v in canais_declarados(_id_orcid(c['ORCID']))[0].items()}),
                'PUBLIC_CHANNELS_SOURCE': 'ORCID researcher-urls (declarado pela pessoa)',
                'PUBLIC_CHANNELS_DECLARED_COUNT': len(
                    canais_declarados(_id_orcid(c['ORCID']))[1]),
                'TECHNICAL_SPEAKER_SENSOR_STATE': (
                    'IDENTITY_PROVED' if ident['IDENTITY_STATE'] == 'IDENTITY_PROVED'
                    else ident['IDENTITY_STATE']),
                **ident,
            })
        # PROVADA conta os dois estados que sustentam o par: o que tem duas fontes
        # concordando no país, e o que tem fonte única e DIZ que é fonte única. Não conta
        # país divergente nem vínculo encerrado.
        provadas = sum(1 for p in pessoas
                       if p['CASE_ID'] == caso_id
                       and p['IDENTITY_STATE'].startswith('IDENTITY_PROVED'))
        blocos[caso_id] = {
            'COUNTRY': pais, 'CROP': crop, 'ISSUE': issue,
            'CANDIDATES': len(cands), 'ELIGIBLE': n_eleg,
            'ATTEMPTED': len(sel), 'PROVED': provadas,
            'CONFLATION_CAP_DERIVED': teto,
            'REFUSALS_BY_REASON': recusa,
            'COVERAGE_STATE': 'NO_IDENTITY' if not sel else (
                'IDENTITY_PROVED' if provadas else 'IDENTITY_NOT_PROVED'),
        }

    estados = {}
    for p in pessoas:
        estados[p['IDENTITY_STATE']] = estados.get(p['IDENTITY_STATE'], 0) + 1
    acordo = {}
    for p in pessoas:
        acordo[p['INSTITUTION_AGREEMENT']] = acordo.get(p['INSTITUTION_AGREEMENT'], 0) + 1

    corpo = {
        'SOURCE_ID': 'SPEAKER-UNIVERSE-PILOT-V1',
        'source': ('derivado: fila espanhola já publicada + OpenAlex (rota gratuita) para '
                   'IT e FR, com cada ORCID conferido contra pub.orcid.org'),
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'NÃO SEI — afiliação de autor não é geografia de estudo',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_IDENTITY',
        'captured_at': None,          # preenchido pelo chamador, nunca por relógio local
        'O_QUE_ISTO_E': ('o universo de PESSOAS do piloto EARLY SIGNAL, por RECORTE '
                         'congelado, com identidade resolvida antes de qualquer execução '
                         'paga. Não é coleta de voz.'),
        'O_QUE_ISTO_NAO_E': [
            'não é ranking — não há score, não há seguidores, não há autoridade',
            'não é prova de que estas pessoas falam publicamente: canal está NOT_TESTED',
            'não é geografia de fato: a afiliação é do autor, não do experimento',
            'não é o censo de pesquisadores dos três países — é um recorte declarado',
            'não é ainda TECHNICAL_SPEAKER_SENSOR: identidade provada é o PRIMEIRO estado',
        ],
        'FROZEN_CASES': [c[0] for c in CASOS],
        'FROZEN_BY': 'aba ÁRBITRA, 2026-08-30, ANTES da coleta',
        'ORDER_ENFORCED': 'RECORTE -> IDENTIDADE -> CANAL PÚBLICO -> CONTEÚDO',
        'CHECKPOINT': {
            'RULE': 'parar em ~%d identidades PROVADAS, distribuídas entre os 6' % META_PROVADAS,
            'ATTEMPTS_PER_CASE': por_caso,
        },
        'CRITERIA': {
            'ORCID': 'presente no registro de autor E resolvido em pub.orcid.org',
            'INSTITUTION': 'declarada, nunca NÃO SEI',
            'RECENCY': 'obra em %d ou depois' % ANO_MINIMO,
            'NOT_CONFLATED': 'organizações <= teto derivado da mediana do quadro (10x)',
            'SCOPE': 'a pessoa herda CROP e ISSUE da CONSULTA que a trouxe, nunca do título',
            'REACH': 'seguidores NÃO entram em nenhum critério — FOLLOWERS != AUTHORITY',
        },
        'BY_CASE': blocos,
        'IDENTITY_STATE_DISTRIBUTION': estados,
        'INSTITUTION_AGREEMENT_DISTRIBUTION': acordo,
        'PEOPLE_COUNT': len(pessoas),
        'PEOPLE': pessoas,
    }
    return corpo


def gravar(corpo, captured_at):
    corpo['captured_at'] = captured_at
    corpo['CAPTURED_AT'] = captured_at
    with open(DEST, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return DEST


def resumo():
    with open(DEST, encoding='utf-8') as f:
        d = json.load(f)
    print('%d tentadas · %s' % (d['PEOPLE_COUNT'], d['IDENTITY_STATE_DISTRIBUTION']))
    print()
    print('%-26s %-6s %-5s %-5s %-5s %s' % (
        'RECORTE', 'CAND', 'ELEG', 'TENT', 'PROV', 'ESTADO'))
    for caso, b in d['BY_CASE'].items():
        print('%-26s %-6d %-5d %-5d %-5d %s' % (
            caso, b['CANDIDATES'], b['ELIGIBLE'], b['ATTEMPTED'], b['PROVED'],
            b['COVERAGE_STATE']))
    print()
    # Sem truncar o estado. A primeira versão cortava em 9 letras e
    # `AGREES_IN_PAST_ONLY` aparecia como `AGREES` — o relatório escondia exatamente o
    # caso que o teste tinha pegado.
    for p in d['PEOPLE']:
        print('  %-26s %-24s %-38s pais:%s' % (
            p['CASE_ID'], (p['NAME'] or '')[:24],
            p['IDENTITY_STATE'].replace('IDENTITY_', ''), p['COUNTRY_AGREEMENT']))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'resumo'
    if cmd == 'montar':
        c = montar()
        quando = sys.argv[2] if len(sys.argv) > 2 else '2026-08-30'
        print('gravado em', gravar(c, quando))
        resumo()
    else:
        resumo()
