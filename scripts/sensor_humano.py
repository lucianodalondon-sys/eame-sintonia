#!/usr/bin/env python3
"""
CAMADA DE SENSORES HUMANOS — registro canônico, tier, cobertura e prova de persistência.

    python3 scripts/sensor_humano.py montar
    python3 scripts/sensor_humano.py cobertura
    python3 scripts/sensor_humano.py persistencia
    python3 scripts/sensor_humano.py resumo

O QUE ESTE ARQUIVO É
---------------------
O dono do registro. As rotas de descoberta (`sensor_epmc_it.py`, `sensor_youtube_it.py`,
`sensor_instituicoes_it.py`) produzem CANDIDATOS. Este arquivo decide, contra critério
escrito, quem entra, com que tier e com que recomendação de monitoramento — e grava.

PESSOA != CANAL != ORGANIZAÇÃO
-------------------------------
`ENTITY_KIND` separa `PERSON` de `ORGANIZATION` em todo registro. Um canal é um
`PUBLIC_PROFILE_URL` de um sensor, nunca um sensor a mais. Duas plataformas da mesma
pessoa continuam sendo UM sensor — a lei que `REGRA-DE-COLETA-EXTERNA` já escreveu.

NÃO EXISTE AUTHORITY SCORE AQUI
--------------------------------
`REGRA-DE-COLETA-EXTERNA §6` proíbe, e a proibição é obedecida: `TECHNICAL_AUTHORITY` e
`FIELD_PROXIMITY` são **estados categóricos com base declarada**, não números que ordenam
pessoas. Nada neste arquivo soma pontos, e `FOLLOWERS` não entra em nenhum critério —
`AUDIENCE_SIZE` é gravado como dado descritivo e não é lido por nenhuma regra de tier.

CAPACIDADE DE OBSERVAÇÃO NÃO SAI DO CARGO
-------------------------------------------
A missão é explícita: *não presumir capacidade apenas pelo cargo; provar pelo conteúdo
público*. Aqui isso é executado:

    pesquisador  -> capacidade vem das OBRAS EM ESCOPO, com os IDs das obras anexados
    serviço      -> capacidade vem dos TERMOS QUE A PRÓPRIA PÁGINA DECLARA, verificados
    canal        -> capacidade fica NOT_ESTABLISHED enquanto não houver conteúdo coletado

E conteúdo **não** foi coletado: o SINTONIA SCRAP exige `APIFY_TOKEN`, ausente neste
ambiente. Isso é `NOT_REACHED — NO_KEY`, não "sensor sem sinal".

DONO CANÔNICO — não duplicar pessoa que já existe no repositório
------------------------------------------------------------------
`SPEAKER-UNIVERSE-PILOT-V1.json` já tem gente italiana com identidade resolvida por ORCID.
Quem já está lá entra aqui com `CANONICAL_OWNER` apontando para aquele artefato e o
`PERSON_ID` de lá — não nasce um segundo dono para a mesma pessoa.
"""
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sensor_epmc_it as EP                                              # noqa: E402
from selo_de_amostra import selar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
REGISTRY = os.path.join(DEST, 'REGISTRY.json')
COVERAGE = os.path.join(DEST, 'COVERAGE.json')
PILOTO = os.path.join(ROOT, 'data', 'samples', 'SPEAKER-UNIVERSE-PILOT-V1.json')
UNIVERSO = os.path.join(DEST, 'UNIVERSE.json')

HOJE = time.strftime('%Y-%m-%d')
ANO_CORRENTE = int(time.strftime('%Y'))

# Mínimo de obras da pessoa DENTRO dos recortes da matriz ADAMA para ela ser tratada como
# sensor, e não como coautoria de passagem. O número é declarado aqui e medido, não
# escolhido para caber num alvo: sobre 4.471 autores italianos do corpus, o corte separa
# quem tem o assunto como linha de trabalho de quem assinou um artigo uma vez.
#
# ELE NÃO ORDENA NINGUÉM. Ninguém é "melhor" por ter mais obras, e nenhum campo do
# registro publica esse número como posição. RECORRÊNCIA != AUTORIDADE (§6).
RECORRENCIA_MINIMA = 8

# --------------------------------------------------------------- escopo -> capacidade
# A capacidade é o que a evidência sustenta, não o que o cargo sugere. Cada par
# CROP|ISSUE mapeia para as capacidades que uma obra NAQUELE escopo comprova.
CAPACIDADE_POR_ISSUE = {
    'SEPTORIA': ['DISEASE_PRESSURE'],
    'FUSARIUM_HEAD_BLIGHT': ['DISEASE_PRESSURE', 'CROP_CONDITION'],
    'RUST': ['DISEASE_PRESSURE'],
    'POWDERY_MILDEW': ['DISEASE_PRESSURE'],
    'DOWNY_MILDEW': ['DISEASE_PRESSURE'],
    'SCAB': ['DISEASE_PRESSURE'],
    'BROWN_ROT': ['DISEASE_PRESSURE'],
    'CERCOSPORA': ['DISEASE_PRESSURE'],
    'LATE_BLIGHT': ['DISEASE_PRESSURE'],
    'OLIVE_DISEASE': ['DISEASE_PRESSURE'],
    'TOMATO_DISEASE': ['DISEASE_PRESSURE'],
    'RICE_PROTECTION': ['DISEASE_PRESSURE'],
    'MYCOTOXIN': ['DISEASE_PRESSURE', 'CROP_CONDITION', 'MARKET_CONCERN'],
    'CORN_BORER': ['PEST_PRESSURE'],
    'ROOTWORM': ['PEST_PRESSURE'],
    'APHIDS': ['PEST_PRESSURE'],
    'CODLING_MOTH': ['PEST_PRESSURE', 'APPLICATION_TIMING'],
    'GRAPE_MOTH': ['PEST_PRESSURE', 'APPLICATION_TIMING'],
    'OLIVE_FRUIT_FLY': ['PEST_PRESSURE'],
    'BROWN_MARMORATED_STINK_BUG': ['PEST_PRESSURE'],
    'FLAVESCENCE_DOREE': ['PEST_PRESSURE', 'DISEASE_PRESSURE', 'REGULATORY_INTERPRETATION'],
    'GRASS_WEEDS': ['WEED_PRESSURE'],
    'MAIZE_WEEDS': ['WEED_PRESSURE'],
    'BEET_WEEDS': ['WEED_PRESSURE'],
    'HERBICIDE_RESISTANCE': ['RESISTANCE', 'WEED_PRESSURE'],
    'FUNGICIDE_RESISTANCE': ['RESISTANCE', 'DISEASE_PRESSURE'],
    'FRUIT_THINNING': ['APPLICATION_TIMING', 'MANAGEMENT_CHANGE'],
    'BULLETIN': ['DISEASE_PRESSURE', 'PEST_PRESSURE', 'APPLICATION_TIMING', 'PHENOLOGY'],
    'FIELD_ADVISORY': ['TECHNICAL_DIFFICULTY', 'PRODUCT_USE'],
}

# Termo que a PÁGINA declara -> capacidade que aquele termo sustenta. Nada aqui vem do
# nome da organização; tudo vem do HTML que a rota buscou e gravou.
CAPACIDADE_POR_TERMO = {
    'bollettino': ['DISEASE_PRESSURE', 'PEST_PRESSURE', 'APPLICATION_TIMING', 'PHENOLOGY'],
    'monitoraggio': ['DISEASE_PRESSURE', 'PEST_PRESSURE'],
    'avversit': ['DISEASE_PRESSURE', 'PEST_PRESSURE'],
    'difesa integrata': ['APPLICATION_TIMING', 'PRODUCT_USE'],
    'produzione integrata': ['APPLICATION_TIMING', 'PRODUCT_USE', 'REGULATORY_INTERPRETATION'],
    'assistenza tecnica': ['TECHNICAL_DIFFICULTY', 'PRODUCT_USE'],
    'sperimentazione': ['PRODUCT_USE', 'MANAGEMENT_CHANGE'],
    'centro di saggio': ['PRODUCT_USE'],
    'campo prova': ['PRODUCT_USE', 'CROP_CONDITION'],
    'laboratorio': ['DISEASE_PRESSURE'],
    'fitopatolog': ['DISEASE_PRESSURE'],
    'entomolog': ['PEST_PRESSURE'],
}

# Recomendação por tipo de sensor. É a recomendação que a missão pede que fique GUARDADA;
# nenhum agendamento é criado, porque a arquitetura de agendamento ainda não tem dono.
MONITORAMENTO = {
    'PLANT_HEALTH_SERVICE': 'WEEKLY',
    'PHYTOSANITARY_CONSORTIUM': 'WEEKLY',
    'TRIAL_CENTRE': 'EVENT_DRIVEN',
    'RESEARCH_CENTRE': 'MONTHLY',
    'PUBLIC_RESEARCH': 'MONTHLY',
    'UNIVERSITY': 'MONTHLY',
    'RESEARCHER': 'MONTHLY',
    'COOPERATIVE': 'WEEKLY',
    'PRODUCER_ORGANIZATION': 'WEEKLY',
    'AGRICULTURAL_CONSORTIUM': 'WEEKLY',
    'FARMER_ASSOCIATION': 'MONTHLY',
    'TECHNICAL_MEDIA': 'WEEKLY',
    'AGRONOMIST': 'WEEKLY',
    'FIELD_TECHNICIAN': 'WEEKLY',
    'TECHNICAL_ADVISER': 'WEEKLY',
    'PRODUCER': 'MONTHLY',
    'CREATOR': 'MONTHLY',
    'VETERINARY_PUBLIC_HEALTH': 'DISCOVERY_ONLY',
    'FOOD_INDUSTRY': 'DISCOVERY_ONLY',
}

TIPO_PARA_BUCKET = {
    'RESEARCHER': 'RESEARCHERS',
    'UNIVERSITY': 'RESEARCHERS', 'PUBLIC_RESEARCH': 'RESEARCHERS',
    'RESEARCH_CENTRE': 'RESEARCHERS', 'TRIAL_CENTRE': 'TECHNICIANS',
    'PLANT_HEALTH_SERVICE': 'TECHNICIANS',
    'PHYTOSANITARY_CONSORTIUM': 'TECHNICIANS',
    'AGRONOMIST': 'AGRONOMISTS', 'TECHNICAL_ADVISER': 'AGRONOMISTS',
    'FIELD_TECHNICIAN': 'TECHNICIANS',
    'COOPERATIVE': 'COOPERATIVES', 'PRODUCER_ORGANIZATION': 'COOPERATIVES',
    'AGRICULTURAL_CONSORTIUM': 'COOPERATIVES', 'FARMER_ASSOCIATION': 'COOPERATIVES',
    'PRODUCER': 'PRODUCERS', 'CREATOR': 'CREATORS', 'TECHNICAL_MEDIA': 'CREATORS',
    'DECISION_SUPPORT_SERVICE': 'TECHNICIANS',
    'CROP_PROTECTION': 'TECHNICIANS', 'PLANT_PATHOLOGIST': 'RESEARCHERS',
    'ENTOMOLOGIST': 'RESEARCHERS', 'RESEARCH_ORGANIZATION': 'RESEARCHERS',
    'VITICULTURE': 'PRODUCERS', 'FRUIT_GROWING': 'PRODUCERS',
    'OLIVE_GROWING': 'PRODUCERS', 'WINERY': 'PRODUCERS', 'NURSERY': 'PRODUCERS',
    'CONSORTIUM': 'COOPERATIVES',
}

# Ordem de leitura de um papel AMBÍGUO. O estado AMBIGUOUS permanece em `SENSOR_TYPE` —
# ele não é desfeito. Isto decide apenas em que balde a pessoa é CONTADA no relatório,
# e a regra é declarada para que a contagem não dependa de ordem de dicionário.
PRIORIDADE_AMBIGUO = ('AGRONOMIST', 'TECHNICAL_ADVISER', 'FIELD_TECHNICIAN',
                      'PLANT_PATHOLOGIST', 'ENTOMOLOGIST', 'PLANT_HEALTH_SERVICE',
                      'CONSORTIUM', 'COOPERATIVE', 'RESEARCH_ORGANIZATION',
                      'UNIVERSITY', 'CROP_PROTECTION', 'PRODUCER', 'VITICULTURE',
                      'FRUIT_GROWING', 'OLIVE_GROWING', 'WINERY', 'NURSERY')


def _bucket(tipo):
    if tipo.startswith('AMBIGUOUS:'):
        partes = tipo.split(':', 1)[1].split('|')
        for cand in PRIORIDADE_AMBIGUO:
            if cand in partes:
                return TIPO_PARA_BUCKET.get(cand, 'OTHER')
        return 'OTHER'
    return TIPO_PARA_BUCKET.get(tipo, 'OTHER')


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower().strip()


def _sid(kind, chave):
    """SENSOR_ID estável: mesma pessoa/organização devolve o mesmo id em toda execução."""
    h = hashlib.sha1(_norm(chave).encode('utf-8')).hexdigest()[:10]
    return 'IT-%s-%s' % ('P' if kind == 'PERSON' else 'O', h)


def _vazio():
    """Todo campo do perfil canônico existe SEMPRE. Ausente vira NÃO SEI, nunca some."""
    return {
        'SENSOR_ID': None, 'ENTITY_KIND': None, 'PERSON_NAME': 'NÃO SEI',
        'ROLE': 'NÃO SEI', 'ROLE_BASIS': 'NÃO SEI',
        'ORGANIZATION': 'NÃO SEI', 'ORGANIZATION_ID': 'NÃO SEI',
        'SENSOR_TYPE': 'NÃO SEI', 'COUNTRY': 'IT',
        'REGION_IDS': [], 'REGION_BASIS': 'NÃO SEI',
        'CROP_IDS': [], 'ISSUE_IDS': [], 'SPECIALTIES': [],
        'INSTITUTION_URL': 'NÃO SEI', 'PUBLIC_PROFILE_URLS': [],
        'INSTAGRAM': 'NÃO SEI', 'YOUTUBE': 'NÃO SEI', 'LINKEDIN': 'NÃO SEI',
        'OTHER_CHANNELS': [], 'PUBLICATIONS_URL': 'NÃO SEI',
        'AUTHORITY_CLASS': 'NÃO SEI',
        'FIELD_PROXIMITY': 'NOT_ESTABLISHED', 'FIELD_PROXIMITY_BASIS': 'NÃO SEI',
        'TECHNICAL_AUTHORITY': 'NOT_ESTABLISHED', 'TECHNICAL_AUTHORITY_BASIS': 'NÃO SEI',
        'ADAMA_RELEVANCE_REASON': 'NÃO SEI',
        'DISCOVERED_FROM': 'NÃO SEI', 'DISCOVERY_QUERY': 'NÃO SEI',
        'LAST_CONTENT_DATE': 'NÃO SEI', 'LAST_CONTENT_RELATIVE': 'NÃO SEI',
        'PUBLICATION_FREQUENCY': 'NÃO SEI',
        'COLLECTION_METHOD': 'NÃO SEI',
        'SINTONIA_SCRAP_SUPPORTED': 'NÃO SEI',
        'VIDEO_AVAILABLE': 'NÃO SEI', 'TRANSCRIPTION_RELEVANT': 'NÃO SEI',
        'OBSERVATION_CAPABILITIES': [], 'OBSERVATION_CAPABILITIES_BASIS': 'NOT_ESTABLISHED',
        'OBSERVATION_EVIDENCE': [],
        'MONITORING_RECOMMENDATION': 'DISCOVERY_ONLY',
        'AUDIENCE_SIZE': 'NÃO SEI',
        'INDEPENDENCE_GROUP': 'NÃO SEI', 'NETWORK_RELATIONSHIPS': [],
        'TIER': None, 'TIER_REASON': 'NÃO SEI',
        'CANONICAL_OWNER': 'NÃO SEI',
        'LAST_CHECKED_AT': HOJE, 'PROVENANCE': {}, 'CLIENT_SAFE': None,
    }


# ----------------------------------------------------------------------------- pessoas
def _piloto_italianos():
    """Quem já tem dono canônico no repositório. Chave: nome normalizado."""
    if not os.path.exists(PILOTO):
        return {}
    with open(PILOTO, encoding='utf-8') as f:
        d = json.load(f)
    out = {}
    for p in d.get('PEOPLE', []):
        if (p.get('COUNTRY') or '').upper() != 'IT':
            continue
        # O piloto escreve "F. Quaglino"; o Europe PMC escreve "Fabio Quaglino". Só o
        # SOBRENOME é chave — e a inicial, quando o piloto só a dá. Nome inteiro não bate
        # e casar por similaridade é proibido.
        nome = p.get('NAME') or ''
        partes = _norm(nome).replace('‐', '-').split()
        if not partes:
            continue
        out[partes[-1]] = {
            'PERSON_ID': p.get('PERSON_ID'), 'NAME': nome, 'ORCID': p.get('ORCID'),
            'IDENTITY_STATE': p.get('IDENTITY_STATE'),
            'OWNER': 'SPEAKER-UNIVERSE-PILOT-V1',
            'INITIAL': partes[0][0] if len(partes) > 1 else None,
        }
    return out


def _capacidades(scopes):
    caps = []
    for s in scopes:
        issue = s.split('|', 1)[1] if '|' in s else s
        for c in CAPACIDADE_POR_ISSUE.get(issue, []):
            if c not in caps:
                caps.append(c)
    return caps


def pessoas():
    """Candidatos-pessoa da rota científica, com o portão agronômico aplicado."""
    p = os.path.join(RAW, 'epmc-IT.json')
    if not os.path.exists(p):
        return [], {'STATE': 'FAILED_WITH_REASON', 'REASON': 'epmc-IT.json ausente'}
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    donos = _piloto_italianos()
    saida, motivos = [], Counter()

    for x in d['PEOPLE']:
        afs = x.get('AFFILIATIONS') or [x.get('AFFILIATION_PRIMARY') or '']
        agro, agro_motivo = EP.agro_declarado(afs)
        principal = x.get('AFFILIATION_PRIMARY') or ''
        org, tipo_org = EP.org_de(principal)
        reg, reg_base = EP.regiao_de(principal)

        r = _vazio()
        r['ENTITY_KIND'] = 'PERSON'
        r['PERSON_NAME'] = x['NAME']
        r['SENSOR_ID'] = _sid('PERSON', '%s|%s' % (x['NAME'], org))
        r['ROLE'] = 'RESEARCHER'
        r['ROLE_BASIS'] = ('afiliação institucional declarada em campo estruturado do '
                           'Europe PMC; nunca de prosa livre nem do assunto do trabalho')
        r['ORGANIZATION'] = org
        r['ORGANIZATION_ID'] = _sid('ORGANIZATION', org) if org != 'NÃO SEI' else 'NÃO SEI'
        r['SENSOR_TYPE'] = 'RESEARCHER'
        r['REGION_IDS'] = [] if (reg == 'NÃO SEI' or reg.startswith('AMBIGUOUS')) else [reg]
        r['REGION_BASIS'] = reg_base if r['REGION_IDS'] else (
            'NÃO SEI — %s' % reg_base)
        r['CROP_IDS'] = sorted({s.split('|')[0] for s in x['SCOPES']})
        r['ISSUE_IDS'] = sorted({s.split('|')[1] for s in x['SCOPES']})
        r['SPECIALTIES'] = r['ISSUE_IDS']
        r['PUBLICATIONS_URL'] = ('https://europepmc.org/search?query=AUTH:%%22%s%%22'
                                 % x['NAME'].replace(' ', '%20'))
        r['INSTITUTION_URL'] = 'NÃO SEI'
        r['DISCOVERED_FROM'] = 'SENSOR-HUMANO-IT/EPMC'
        r['DISCOVERY_QUERY'] = sorted(x['SCOPES'])
        r['LAST_CONTENT_DATE'] = x.get('LAST_DATE') or 'NÃO SEI'
        r['PUBLICATION_FREQUENCY'] = '%d obras em escopo na janela %s' % (
            x['WORKS_IN_SCOPE'], d['WINDOW'])
        r['COLLECTION_METHOD'] = 'Europe PMC REST — rota gratuita, sem chave'
        r['SINTONIA_SCRAP_SUPPORTED'] = 'NOT_TESTED — nenhum canal público resolvido'
        r['VIDEO_AVAILABLE'] = 'NÃO SEI'
        r['TRANSCRIPTION_RELEVANT'] = 'NÃO SEI'
        r['TECHNICAL_AUTHORITY'] = ('DECLARED_RESEARCH_AFFILIATION' if agro == 'DECLARED'
                                    else 'NOT_DECLARED')
        r['TECHNICAL_AUTHORITY_BASIS'] = agro_motivo
        r['FIELD_PROXIMITY'] = 'NOT_ESTABLISHED'
        r['FIELD_PROXIMITY_BASIS'] = (
            'nenhum conteúdo público coletado: SINTONIA SCRAP exige APIFY_TOKEN, ausente. '
            'Publicação não prova visita a campo.')
        r['OBSERVATION_CAPABILITIES'] = _capacidades(x['SCOPES'])
        r['OBSERVATION_CAPABILITIES_BASIS'] = (
            'PUBLICATION_IN_SCOPE — derivada do recorte que trouxe a pessoa, com os '
            'identificadores das obras anexados; nunca do cargo')
        r['OBSERVATION_EVIDENCE'] = x.get('WORKS', [])[:4]
        r['AUTHORITY_CLASS'] = 'SCIENCE'
        r['MONITORING_RECOMMENDATION'] = MONITORAMENTO['RESEARCHER']
        r['INDEPENDENCE_GROUP'] = org if org != 'NÃO SEI' else 'UNGROUPED:%s' % r['SENSOR_ID']
        r['CLIENT_SAFE'] = True
        r['PROVENANCE'] = {
            'SOURCE_ID': d['SOURCE_ID'], 'ROUTE': d['source'],
            'CAPTURED_AT': d['CAPTURED_AT'], 'WINDOW': d['WINDOW'],
            'AFFILIATION_PRIMARY': principal,
            'AFFILIATIONS_DISTINCT': x.get('AFFILIATIONS_DISTINCT'),
            'ORCID_DECLARED': x.get('ORCID'),
            'ORCID_STATE': 'ORCID_DECLARED_NOT_RESOLVED' if x.get('ORCID')
                           else 'NO_ORCID_IN_INDEX',
            'AGRO_AFFILIATION': agro, 'AGRO_AFFILIATION_REASON': agro_motivo,
            'WORKS_IN_SCOPE': x['WORKS_IN_SCOPE'],
        }
        # dono canônico: sobrenome bate E a inicial do piloto bate quando o piloto só deu
        # a inicial. Sem os dois, não se declara a mesma pessoa.
        sob = _norm(x['NAME']).replace('‐', '-').split()
        dono = donos.get(sob[-1]) if sob else None
        if dono and (dono['INITIAL'] is None or (sob and sob[0][0] == dono['INITIAL'])):
            r['CANONICAL_OWNER'] = dono['OWNER']
            r['PROVENANCE']['CANONICAL_PERSON_ID'] = dono['PERSON_ID']
            r['PROVENANCE']['CANONICAL_OWNER_NAME'] = dono['NAME']
            r['PROVENANCE']['CANONICAL_IDENTITY_STATE'] = dono['IDENTITY_STATE']
            r['PROVENANCE']['CANONICAL_MATCH_BASIS'] = (
                'sobrenome idêntico + inicial do prenome; nenhum casamento por similaridade')
        r['ADAMA_RELEVANCE_REASON'] = (
            'publica em %s x %s — pares presentes na matriz ADAMA Itália (UNIVERSE.json)'
            % ('/'.join(r['CROP_IDS'][:3]), '/'.join(r['ISSUE_IDS'][:3])))
        r['_WORKS'] = x['WORKS_IN_SCOPE']
        r['_ORCID'] = x.get('ORCID')
        r['_AGRO'] = agro
        motivos[agro] += 1
        saida.append(r)
    return saida, {'STATE': 'READ', 'AGRO_GATE': dict(motivos),
                   'CANDIDATES': len(saida), 'SOURCE': d['SOURCE_ID']}


# ---------------------------------------------------------------------- organizações
def organizacoes():
    p = os.path.join(RAW, 'institutions-IT.json')
    if not os.path.exists(p):
        return [], {'STATE': 'FAILED_WITH_REASON', 'REASON': 'institutions-IT.json ausente'}
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    saida = []
    for o in d['ORGANIZATIONS']:
        termos = o.get('ROLE_TERMS_DECLARED') or []
        caps = []
        for t in termos:
            for c in CAPACIDADE_POR_TERMO.get(t, []):
                if c not in caps:
                    caps.append(c)
        tipo = o['DECLARED_TYPE']
        r = _vazio()
        r['ENTITY_KIND'] = 'ORGANIZATION'
        r['SENSOR_ID'] = _sid('ORGANIZATION', o['ORGANIZATION'])
        r['PERSON_NAME'] = 'NOT_APPLICABLE — ENTITY_KIND=ORGANIZATION'
        r['ROLE'] = tipo
        r['ROLE_BASIS'] = ('tipo declarado pela própria página institucional; termos de '
                           'papel encontrados no HTML buscado nesta execução')
        r['ORGANIZATION'] = o['ORGANIZATION']
        r['ORGANIZATION_ID'] = r['SENSOR_ID']
        r['SENSOR_TYPE'] = tipo
        r['REGION_IDS'] = [o['REGION']]
        r['REGION_BASIS'] = 'SEDE_DECLARADA_DA_ORGANIZACAO'
        r['CROP_IDS'] = o['CROPS']
        r['ISSUE_IDS'] = []
        r['SPECIALTIES'] = termos
        r['INSTITUTION_URL'] = o['INSTITUTION_URL']
        r['PUBLIC_PROFILE_URLS'] = [o['INSTITUTION_URL']]
        r['DISCOVERED_FROM'] = 'SENSOR-HUMANO-IT/INSTITUTIONS'
        r['DISCOVERY_QUERY'] = 'matriz ADAMA Itália: cultura x região'
        r['COLLECTION_METHOD'] = 'GET direto na página institucional'
        r['SINTONIA_SCRAP_SUPPORTED'] = 'NOT_TESTED'
        r['TECHNICAL_AUTHORITY'] = ('DECLARED_TECHNICAL_ROLE' if termos else 'NOT_DECLARED')
        r['TECHNICAL_AUTHORITY_BASIS'] = ('termos declarados na página: %s'
                                          % ', '.join(termos[:6]) if termos
                                          else 'nenhum termo de papel técnico no HTML lido')
        campo = [t for t in termos if t in ('bollettino', 'monitoraggio', 'avversit',
                                            'assistenza tecnica', 'campo prova',
                                            'centro di saggio', 'difesa integrata')]
        r['FIELD_PROXIMITY'] = 'DECLARED_TERRITORIAL_ACTIVITY' if campo else 'NOT_ESTABLISHED'
        r['FIELD_PROXIMITY_BASIS'] = ('a própria página declara: %s' % ', '.join(campo)
                                      if campo else
                                      'nenhum termo de atividade territorial declarado')
        r['OBSERVATION_CAPABILITIES'] = caps
        r['OBSERVATION_CAPABILITIES_BASIS'] = (
            'DECLARED_ON_INSTITUTIONAL_PAGE — termos lidos do HTML buscado, não do nome '
            'da organização' if caps else 'NOT_ESTABLISHED')
        r['OBSERVATION_EVIDENCE'] = [{'URL': o['INSTITUTION_URL'],
                                      'PAGE_TITLE': o.get('PAGE_TITLE'),
                                      'HTTP_STATUS': o.get('HTTP_STATUS'),
                                      'TERMS': termos}]
        r['AUTHORITY_CLASS'] = ('INSTITUTIONAL' if tipo in (
            'PLANT_HEALTH_SERVICE', 'PUBLIC_RESEARCH', 'RESEARCH_CENTRE', 'UNIVERSITY',
            'PHYTOSANITARY_CONSORTIUM', 'TRIAL_CENTRE') else 'SECTORAL')
        r['ADAMA_RELEVANCE_REASON'] = o['ADAMA_RELEVANCE_REASON']
        r['MONITORING_RECOMMENDATION'] = MONITORAMENTO.get(tipo, 'DISCOVERY_ONLY')
        r['INDEPENDENCE_GROUP'] = o['ORGANIZATION']
        r['CLIENT_SAFE'] = True
        r['LAST_CONTENT_DATE'] = 'NÃO SEI'
        r['PROVENANCE'] = {
            'SOURCE_ID': d['SOURCE_ID'], 'ROUTE': d['source'],
            'CAPTURED_AT': d['CAPTURED_AT'], 'URL_STATE': o['URL_STATE'],
            'HTTP_STATUS': o['HTTP_STATUS'], 'FAILURE_REASON': o.get('FAILURE_REASON'),
            'PAGE_TITLE': o.get('PAGE_TITLE'), 'PAGE_BYTES': o.get('PAGE_BYTES'),
        }
        r['_URL_OK'] = o['URL_STATE'] == 'VERIFIED'
        r['_TERMS'] = len(termos)
        saida.append(r)
    return saida, {'STATE': 'READ', 'CANDIDATES': len(saida),
                   'VERIFIED': d['VERIFIED'], 'FAILED': d['FAILED'],
                   'SOURCE': d['SOURCE_ID']}


# ---------------------------------------------------------------------------- canais
def canais():
    p = os.path.join(RAW, 'youtube-IT.json')
    if not os.path.exists(p):
        return [], {'STATE': 'FAILED_WITH_REASON', 'REASON': 'youtube-IT.json ausente'}
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    saida = []
    for c in d['CHANNELS']:
        if 'ABOUT_STATE' not in c:
            continue                                  # identidade não resolvida: não entra
        papel = c.get('DECLARED_ROLE') or 'NOT_DECLARED'
        pais = c.get('DECLARED_COUNTRY') or 'NOT_DECLARED'
        r = _vazio()
        r['ENTITY_KIND'] = 'ORGANIZATION' if papel in (
            'RESEARCH_ORGANIZATION', 'UNIVERSITY', 'CONSORTIUM', 'COOPERATIVE',
            'PLANT_HEALTH_SERVICE', 'WINERY') else 'PERSON_OR_ORGANIZATION_NOT_DECLARED'
        r['SENSOR_ID'] = _sid('CHANNEL', c['CHANNEL_PATH'])
        r['PERSON_NAME'] = 'NÃO SEI — o nome do canal não é nome de pessoa'
        r['ROLE'] = papel
        r['ROLE_BASIS'] = c.get('DECLARED_ROLE_BASIS') or 'NÃO SEI'
        r['ORGANIZATION'] = 'NÃO SEI'
        r['SENSOR_TYPE'] = papel if papel != 'NOT_DECLARED' else 'NOT_DECLARED'
        r['COUNTRY'] = pais
        r['CROP_IDS'] = sorted({s.split('|')[0] for s in c['SCOPES']})
        r['ISSUE_IDS'] = sorted({s.split('|')[1] for s in c['SCOPES']})
        r['SPECIALTIES'] = r['ISSUE_IDS']
        r['YOUTUBE'] = c['CHANNEL_URL']
        r['PUBLIC_PROFILE_URLS'] = [c['CHANNEL_URL']] + (c.get('EXTERNAL_LINKS') or [])
        r['OTHER_CHANNELS'] = c.get('EXTERNAL_LINKS') or []
        r['DISCOVERED_FROM'] = 'SENSOR-HUMANO-IT/YOUTUBE-DISCOVERY'
        r['DISCOVERY_QUERY'] = c.get('DISCOVERY_QUERIES')
        r['LAST_CONTENT_DATE'] = 'NÃO SEI — a busca devolve tempo relativo, não data'
        r['LAST_CONTENT_RELATIVE'] = [
            s.get('PUBLISHED_RELATIVE') for s in (c.get('SAMPLE_VIDEOS') or [])]
        r['AUDIENCE_SIZE'] = c.get('SUBSCRIBERS_TEXT') or 'NÃO SEI'
        r['PUBLICATION_FREQUENCY'] = c.get('VIDEOS_TEXT') or 'NÃO SEI'
        r['COLLECTION_METHOD'] = 'youtube.com/results + aba About — rota pública gratuita'
        r['SINTONIA_SCRAP_SUPPORTED'] = (
            'YES_BY_ARCHITECTURE / NOT_REACHED_NOW — scripts/sensor_coleta.py e '
            'scripts/youtube_transcrever.py cobrem este canal, mas exigem APIFY_TOKEN')
        r['VIDEO_AVAILABLE'] = 'YES — canal de vídeo'
        r['TRANSCRIPTION_RELEVANT'] = 'YES — a fala é a camada que a missão prioriza'
        r['TECHNICAL_AUTHORITY'] = ('DECLARED_IN_CHANNEL_DESCRIPTION'
                                    if papel != 'NOT_DECLARED' else 'NOT_DECLARED')
        r['TECHNICAL_AUTHORITY_BASIS'] = r['ROLE_BASIS']
        r['FIELD_PROXIMITY'] = 'NOT_ESTABLISHED'
        r['FIELD_PROXIMITY_BASIS'] = (
            'nenhum conteúdo coletado nem transcrito — NOT_REACHED por falta de chave. '
            'A missão proíbe presumir capacidade pelo rótulo do canal.')
        r['OBSERVATION_CAPABILITIES'] = []
        r['OBSERVATION_CAPABILITIES_BASIS'] = (
            'NOT_ESTABLISHED — exige conteúdo público coletado e transcrito')
        r['AUTHORITY_CLASS'] = 'PUBLIC_CHANNEL'
        r['ADAMA_RELEVANCE_REASON'] = (
            'canal aparece em consultas técnicas italianas de %s' % '/'.join(r['ISSUE_IDS'][:3]))
        r['MONITORING_RECOMMENDATION'] = MONITORAMENTO.get(papel, 'DISCOVERY_ONLY')
        r['INDEPENDENCE_GROUP'] = 'CHANNEL:%s' % c['CHANNEL_PATH']
        r['CLIENT_SAFE'] = True
        r['PROVENANCE'] = {
            'SOURCE_ID': d['SOURCE_ID'], 'ROUTE': d['source'],
            'CAPTURED_AT': d['CAPTURED_AT'], 'CHANNEL_NAME': c['CHANNEL_NAME'],
            'ABOUT_STATE': c['ABOUT_STATE'], 'ABOUT_REASON': c.get('ABOUT_REASON'),
            'DECLARED_COUNTRY_RAW': c.get('DECLARED_COUNTRY_RAW'),
            'DESCRIPTION_READ': bool(c.get('DESCRIPTION')),
            'IS_INDUSTRY': c.get('IS_INDUSTRY'),
            'HITS_IN_DISCOVERY': c.get('HITS'),
        }
        r['_CHANNEL_NAME'] = c['CHANNEL_NAME']
        r['_INDUSTRY'] = bool(c.get('IS_INDUSTRY'))
        r['_HITS'] = c.get('HITS', 0)
        saida.append(r)
    return saida, {'STATE': 'READ', 'CANDIDATES': len(saida),
                   'RESOLVED': d.get('IDENTITY_RESOLVED_COUNT'),
                   'PENDING': d.get('IDENTITY_PENDING_COUNT'),
                   'SOURCE': d['SOURCE_ID']}


# ------------------------------------------------------------------------------ tier
def _tier(r):
    """TIER por critério escrito. Nenhum número ordena pessoas; nenhum critério lê alcance."""
    kind, tipo = r['ENTITY_KIND'], r['SENSOR_TYPE']

    if r['DISCOVERED_FROM'] == 'SENSOR-HUMANO-IT/EPMC':
        # Os quatro portões da rota científica. Nenhum deles ORDENA pessoas — todos
        # decidem INCLUSÃO, e a diferença importa: `REGRA-DE-COLETA §6` proíbe authority
        # score, e RECORRÊNCIA NÃO É AUTORIDADE. `RECORRENCIA_MINIMA` diz apenas "este é
        # o assunto desta pessoa, não uma coautoria de passagem".
        if r.get('_AGRO') != 'DECLARED' and r['CANONICAL_OWNER'] == 'NÃO SEI':
            return 'REJECT', ('afiliação declarada não é agronômica — %s. Autor real do '
                              'assunto, sensor agrícola não: %s'
                              % (r.get('_AGRO'), r['TECHNICAL_AUTHORITY_BASIS']))
        # A exceção não afrouxa o portão: ela reconhece prova que já existe nesta casa.
        # `Nicola Mori` declara "Department of Biotechnology, University of Verona" — sem
        # marcador agronômico nenhum. Mas ele já está no `SPEAKER-UNIVERSE-PILOT-V1` com
        # `IDENTITY_PROVED` por ORCID e escopo IT-VINE-FLAVESCENCE congelado por árbitro.
        # Barrá-lo aqui seria o registro desconhecendo a própria prova anterior.
        if r.get('_AGRO') != 'DECLARED':
            r['TECHNICAL_AUTHORITY'] = 'PROVED_BY_CANONICAL_OWNER'
            r['TECHNICAL_AUTHORITY_BASIS'] = (
                'afiliação atual não declara domínio agronômico (%s), mas a pessoa tem '
                'dono canônico em %s com identidade resolvida por ORCID'
                % (r.get('_AGRO'), r['CANONICAL_OWNER']))
        if r['ORGANIZATION'] == 'NÃO SEI':
            return 'REJECT', ('afiliação agronômica declarada mas organização não '
                              'resolvida no vocabulário canônico — sem ORGANIZATION_ID '
                              'não há família de origem, e sem família não há medida de '
                              'independência (§11)')
        recente = (r['LAST_CONTENT_DATE'] or '')[:4]
        if not (recente.isdigit() and int(recente) >= ANO_CORRENTE - 1):
            return 'REJECT', ('sem obra no recorte desde %s — a pergunta desta camada é '
                              'quem observa HOJE' % (ANO_CORRENTE - 1))
        if r['_WORKS'] < RECORRENCIA_MINIMA:
            return 'REJECT', ('%d obra(s) no recorte ADAMA, abaixo do mínimo de %d — '
                              'coautoria de passagem não é sensor. Fica no DISCOVERY_POOL'
                              % (r['_WORKS'], RECORRENCIA_MINIMA))
        if not r['_ORCID'] and r['CANONICAL_OWNER'] == 'NÃO SEI':
            # `REGRA-DE-COLETA §17`, medido na Espanha: o elo CIÊNCIA -> CANAL PÚBLICO não
            # se constrói com nome, e casar por similaridade produziu falso positivo
            # demonstrável. Sem identificador declarado que atravesse camadas, esta pessoa
            # nunca poderá ser ligada a um canal — logo não pode ser monitorada.
            return 'REJECT', ('sem ORCID declarado no índice — §17 exige identificador '
                              'declarado que atravesse camadas; sem ele o elo '
                              'CIÊNCIA -> CANAL PÚBLICO não se constrói e a pessoa não '
                              'pode virar sensor monitorável. Fica no DISCOVERY_POOL')
        if int(recente) >= ANO_CORRENTE:
            return 'A', ('instituição agronômica nomeada (%s), %d obras nos recortes ADAMA, '
                         'ORCID declarado e obra em %s'
                         % (r['ORGANIZATION'], r['_WORKS'], recente))
        return 'B', ('instituição agronômica nomeada e ORCID declarado, %d obras no '
                     'recorte, mas última obra em %s e não em %d'
                     % (r['_WORKS'], recente, ANO_CORRENTE))

    if r['DISCOVERED_FROM'] == 'SENSOR-HUMANO-IT/INSTITUTIONS':
        if not r.get('_URL_OK'):
            return 'C', ('URL não verificada nesta execução (%s) — organização real, '
                         'rota não provada' % r['PROVENANCE'].get('FAILURE_REASON'))
        if r['FIELD_PROXIMITY'] == 'DECLARED_TERRITORIAL_ACTIVITY' and r['_TERMS'] >= 4:
            return 'A', ('página verificada declara atividade territorial (%s) e %d termos '
                         'de papel técnico' % (r['FIELD_PROXIMITY_BASIS'], r['_TERMS']))
        if r['_TERMS'] >= 2:
            return 'B', ('página verificada com %d termos de papel técnico, sem atividade '
                         'territorial declarada' % r['_TERMS'])
        return 'C', 'página verificada, mas declara pouco ou nenhum papel técnico'

    if r['DISCOVERED_FROM'] == 'SENSOR-HUMANO-IT/YOUTUBE-DISCOVERY':
        if r.get('_INDUSTRY'):
            return 'REJECT', ('canal de indústria de defensivos — pertence à camada '
                              'COMPETITOR COMMUNICATION, não a sensores humanos')
        if r['COUNTRY'] != 'IT':
            return 'REJECT', ('país declarado é "%s" — idioma não é país, e a missão é '
                              'Itália' % r['COUNTRY'])
        if r['ROLE'] == 'NOT_DECLARED':
            return 'REJECT', ('canal não declara papel técnico na própria descrição; '
                              'nome de canal não decide papel')
        if r['ROLE'].startswith('AMBIGUOUS'):
            return 'C', ('papel declarado é ambíguo (%s) — estado, não empate a desfazer'
                         % r['ROLE'])
        return 'C', ('papel técnico declarado pelo canal, mas nenhum conteúdo coletado ou '
                     'transcrito: proximidade de campo e capacidade seguem NOT_ESTABLISHED')

    return 'C', 'rota não classificada'


def montar():
    os.makedirs(DEST, exist_ok=True)
    ps, mp = pessoas()
    os_, mo = organizacoes()
    cs, mc = canais()
    todos = ps + os_ + cs
    for r in todos:
        r['TIER'], r['TIER_REASON'] = _tier(r)

    aceitos = [r for r in todos if r['TIER'] != 'REJECT']
    # Um sensor rejeitado não some: o motivo da rejeição é evidência, e some-lo tornaria
    # indistinguível "avaliado e recusado" de "nunca visto".
    rejeitados = [{'SENSOR_ID': r['SENSOR_ID'], 'ENTITY_KIND': r['ENTITY_KIND'],
                   'NAME': r.get('_CHANNEL_NAME') or r['PERSON_NAME'] or r['ORGANIZATION'],
                   'ORGANIZATION': r['ORGANIZATION'],
                   'DISCOVERED_FROM': r['DISCOVERED_FROM'],
                   'TIER': 'REJECT', 'TIER_REASON': r['TIER_REASON']} for r in todos
                  if r['TIER'] == 'REJECT']

    # relações de rede: mesma organização = mesma família de origem (§11)
    porg = defaultdict(list)
    for r in aceitos:
        porg[r['INDEPENDENCE_GROUP']].append(r['SENSOR_ID'])
    for r in aceitos:
        irmaos = [s for s in porg[r['INDEPENDENCE_GROUP']] if s != r['SENSOR_ID']]
        r['NETWORK_RELATIONSHIPS'] = [
            {'RELATION': 'SAME_ORGANIZATION', 'SENSOR_ID': s} for s in irmaos[:12]]
        r['INDEPENDENCE_NOTE'] = (
            '%d sensores compartilham esta origem — contam como UMA família de origem '
            'em qualquer convergência' % len(porg[r['INDEPENDENCE_GROUP']]))

    # DISCOVERY_POOL — quem foi barrado por UM portão só, e por qual. Não é sensor, e não
    # é lixo: é a fila da próxima rodada, com o que falta escrito em cada linha.
    pool = []
    for r in todos:
        if r['TIER'] != 'REJECT':
            continue
        motivo = r['TIER_REASON']
        falta = ('ORCID' if 'sem ORCID declarado' in motivo else
                 'RECURRENCE' if 'abaixo do mínimo' in motivo else
                 'ORGANIZATION_VOCABULARY' if 'organização não resolvida' in motivo else
                 'CHANNEL_ROLE_DECLARATION' if 'não declara papel técnico' in motivo else
                 None)
        if falta is None:
            continue
        pool.append({
            'NAME': r.get('_CHANNEL_NAME') or r['PERSON_NAME'] or r['ORGANIZATION'],
            'ORGANIZATION': r['ORGANIZATION'], 'REGION_IDS': r['REGION_IDS'],
            'CROP_IDS': r['CROP_IDS'], 'ISSUE_IDS': r['ISSUE_IDS'],
            'MISSING': falta, 'REASON': motivo,
            'WORKS_IN_SCOPE': (r['PROVENANCE'] or {}).get('WORKS_IN_SCOPE'),
            'DISCOVERED_FROM': r['DISCOVERED_FROM'],
            'WHAT_WOULD_RESOLVE_IT': {
                'ORCID': 'resolver o ORCID da pessoa em pub.orcid.org por instituição + '
                         'sobrenome, e só promover se a fonte responder',
                'RECURRENCE': 'ampliar a janela do recorte ou abrir um recorte novo onde '
                              'esta pessoa seja recorrente, não afrouxar o mínimo',
                'ORGANIZATION_VOCABULARY': 'acrescentar a organização ao vocabulário '
                                           'canônico de ORG_CANONICA, com o nome como '
                                           'ela aparece na afiliação declarada',
                'CHANNEL_ROLE_DECLARATION': 'ler a aba About de novo, ou buscar o papel '
                                            'num perfil institucional declarado — nunca '
                                            'inferir papel do conteúdo do vídeo',
            }[falta],
        })
    # O recorte é ESTRATIFICADO por motivo, não um top-N global. Ordenar tudo por obras e
    # cortar em 120 fazia os 79 canais — que não têm contagem de obras — desaparecerem do
    # arquivo, embora contados em DISCOVERY_POOL_BY_MISSING. Uma categoria que some da
    # amostra é indistinguível de uma categoria vazia.
    pool.sort(key=lambda x: (x['MISSING'], -(x.get('WORKS_IN_SCOPE') or 0), x['NAME']))
    por_motivo = defaultdict(list)
    for x in pool:
        por_motivo[x['MISSING']].append(x)
    amostra = [x for m in sorted(por_motivo) for x in por_motivo[m][:30]]
    amostra.sort(key=lambda x: -(x.get('WORKS_IN_SCOPE') or 0))

    for r in todos:
        for k in [k for k in r if k.startswith('_')]:
            r.pop(k)

    tiers = Counter(r['TIER'] for r in aceitos)
    tipos = Counter(_bucket(r['SENSOR_TYPE']) for r in aceitos)
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/REGISTRY',
        'source': 'derivado das rotas EPMC + INSTITUTIONS + YOUTUBE-DISCOVERY',
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_IDENTITY',
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'O_QUE_ISTO_E': 'a rede de sensores humanos italiana do SINTONIA: quem observa, '
                        'sobre que cultura, que problema, em que região, e quando voltar',
        'O_QUE_ISTO_NAO_E': [
            'não é ranking — nenhum campo ordena pessoas e AUDIENCE_SIZE não entra em '
            'nenhum critério de tier',
            'não é prova de que o sensor observou o campo — FIELD_PROXIMITY sai '
            'NOT_ESTABLISHED onde não há conteúdo coletado',
            'não é sinal — sinal exige conteúdo, e conteúdo exige a rota paga',
            'não é lista de influenciadores — INFLUENCER=AUTHORITY não existe no modelo',
        ],
        'CONTENT_COLLECTION_STATE': 'NOT_REACHED — NO_KEY',
        'CONTENT_COLLECTION_REASON':
            'o SINTONIA SCRAP (scripts/sensor_coleta.py, youtube_transcrever.py, '
            'instagram_coleta.py) exige APIFY_TOKEN; nenhuma variável APIFY* existe neste '
            'ambiente (medido 2026-09-04). Sem coleta não há OBSERVATION_CAPABILITIES '
            'provada por fala, e nenhuma foi inventada.',
        'ROUTES': {'EPMC': mp, 'INSTITUTIONS': mo, 'YOUTUBE': mc},
        'DISCOVERED': len(todos),
        'QUALIFIED': len(aceitos),
        'REJECTED': len(rejeitados),
        'BY_TIER': dict(tiers),
        'BY_TYPE': dict(tipos),
        'BY_ENTITY_KIND': dict(Counter(r['ENTITY_KIND'] for r in aceitos)),
        'BY_CROP': dict(Counter(c for r in aceitos for c in r['CROP_IDS']).most_common()),
        'BY_REGION': dict(Counter(g for r in aceitos for g in r['REGION_IDS']).most_common()),
        'BY_MONITORING': dict(Counter(r['MONITORING_RECOMMENDATION'] for r in aceitos)),
        'INDEPENDENT_ORIGIN_FAMILIES': len(porg),
        'BY_BUCKET_AND_TIER': {b: dict(Counter(
            r['TIER'] for r in aceitos if _bucket(r['SENSOR_TYPE']) == b))
            for b in sorted({_bucket(r['SENSOR_TYPE']) for r in aceitos})},
        'DISCOVERY_POOL_COUNT': len(pool),
        'DISCOVERY_POOL_BY_MISSING': dict(Counter(x['MISSING'] for x in pool)),
        'SENSORS': aceitos,
        'DISCOVERY_POOL_SAMPLE_RULE': 'até 30 por motivo — amostra estratificada, '
                                     'nunca um top-N global que apaga uma categoria',
        'DISCOVERY_POOL': amostra,
        'REJECTED_SENSORS': rejeitados,
    }
    with open(REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('descobertos %d · qualificados %d · rejeitados %d' % (
        len(todos), len(aceitos), len(rejeitados)))
    print('tiers %s' % dict(tiers))
    print('tipos %s' % dict(tipos))
    print('famílias de origem independentes: %d' % len(porg))
    print('-> %s' % REGISTRY)
    return corpo


# ------------------------------------------------------------------ matriz de cobertura
def cobertura():
    """CROP x REGION x SPECIALTY, com GOOD / WEAK / NONE. Mede onde ainda estamos cegos.

    A régua é declarada e derivada, nunca digitada:

        GOOD  ao menos 2 sensores Tier A/B, de ao menos 2 FAMÍLIAS DE ORIGEM distintas
        WEAK  há sensor, mas só um, ou todos da mesma família de origem
        NONE  nenhum sensor qualificado nessa célula

    A exigência de duas famílias vem do §11 da missão e da lei de independência: três
    pessoas do mesmo laboratório não são três fontes. Uma célula coberta por um único
    instituto é WEAK por construção, mesmo com cinco nomes dentro.
    """
    with open(REGISTRY, encoding='utf-8') as f:
        reg = json.load(f)
    with open(UNIVERSO, encoding='utf-8') as f:
        uni = json.load(f)

    celulas = {}
    for linha in uni['MATRIX']:
        for regiao in linha['REGIONS_TO_SEARCH']:
            celulas[(linha['CROP'], regiao, linha['TARGET'])] = {
                'CROP': linha['CROP'], 'REGION': regiao, 'SPECIALTY': linha['TARGET'],
                'ADAMA_ANCHOR': linha['ADAMA_ANCHOR'], 'BASIS': linha['BASIS'],
                'SENSORS': [], 'FAMILIES': set(),
            }

    # QUANTO DA COBERTURA É A REGRA, E NÃO O SENSOR — 2026-09-04
    # -----------------------------------------------------------
    # A expansão territorial abaixo é honesta e está declarada em comentário desde sempre.
    # O problema é outro: ela NÃO estava no campo `RULE` do artefato publicado, e ela é
    # responsável por mais da metade do número. Medido: 72 células GOOD com ela, 30 sem.
    #
    #     UM NÚMERO QUE DEPENDE DE UMA REGRA PRECISA CARREGAR A REGRA.
    #
    # Por isso a passada agora é feita duas vezes e o artefato publica as duas contagens.
    # Nenhum limiar mudou; o que mudou é que agora dá para ver de onde vem o 72.
    sem_expansao = {k: {'S': 0, 'F': set()} for k in celulas}
    for s in reg['SENSORS']:
        if s['TIER'] not in ('A', 'B'):
            continue
        for crop in s['CROP_IDS']:
            for regiao in s['REGION_IDS']:
                for alvo in (s['ISSUE_IDS'] or []):
                    c = sem_expansao.get((crop, regiao, alvo))
                    if c is not None:
                        c['S'] += 1
                        c['F'].add(s['INDEPENDENCE_GROUP'])
    for s in reg['SENSORS']:
        if s['TIER'] not in ('A', 'B'):
            continue
        for crop in s['CROP_IDS']:
            for regiao in s['REGION_IDS']:
                # Sensor sem ISSUE declarado (organização territorial) cobre TODAS as
                # especialidades da sua cultura naquela região: o bollettino territorial
                # é, por construção, multi-alvo. Isso está declarado, não presumido.
                alvos = s['ISSUE_IDS'] or [k[2] for k in celulas
                                           if k[0] == crop and k[1] == regiao]
                for alvo in alvos:
                    c = celulas.get((crop, regiao, alvo))
                    if c is None:
                        continue
                    c['SENSORS'].append({'SENSOR_ID': s['SENSOR_ID'],
                                         'NAME': s['PERSON_NAME'] if s['ENTITY_KIND'] == 'PERSON'
                                                 else s['ORGANIZATION'],
                                         'TIER': s['TIER'],
                                         'FAMILY': s['INDEPENDENCE_GROUP']})
                    c['FAMILIES'].add(s['INDEPENDENCE_GROUP'])

    saida = []
    for c in celulas.values():
        n, fam = len(c['SENSORS']), len(c['FAMILIES'])
        estado = ('GOOD' if (n >= 2 and fam >= 2) else
                  ('WEAK' if n >= 1 else 'NONE'))
        motivo = ('%d sensores Tier A/B em %d famílias de origem' % (n, fam) if n else
                  'nenhum sensor qualificado nesta célula')
        saida.append({'CROP': c['CROP'], 'REGION': c['REGION'],
                      'SPECIALTY': c['SPECIALTY'], 'STATE': estado, 'REASON': motivo,
                      'SENSOR_COUNT': n, 'ORIGIN_FAMILIES': fam,
                      'ADAMA_ANCHOR': c['ADAMA_ANCHOR'], 'BASIS': c['BASIS'],
                      'SENSORS': c['SENSORS'][:8]})
    saida.sort(key=lambda x: ({'NONE': 0, 'WEAK': 1, 'GOOD': 2}[x['STATE']],
                              x['CROP'], x['REGION'], x['SPECIALTY']))

    est = Counter(x['STATE'] for x in saida)
    por_crop = defaultdict(Counter)
    for x in saida:
        por_crop[x['CROP']][x['STATE']] += 1
    por_regiao = defaultdict(Counter)
    for x in saida:
        por_regiao[x['REGION']][x['STATE']] += 1

    lacunas = [x for x in saida if x['STATE'] == 'NONE']
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/COVERAGE',
        'source': 'derivado de REGISTRY.json x UNIVERSE.json',
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'RULE': ('GOOD = >=2 sensores Tier A/B em >=2 famílias de origem; WEAK = >=1; '
                 'NONE = 0. Família de origem = INDEPENDENCE_GROUP (organização). '
                 'E UMA TERCEIRA REGRA, que responde por mais da metade do GOOD: sensor '
                 'territorial Tier A/B SEM especialidade declarada cobre TODAS as '
                 'especialidades da sua cultura naquela região, porque o bollettino é '
                 'multi-alvo por construção. Sem essa expansão os mesmos dados dão '
                 'GOOD=%d em vez de GOOD=%d — ver BY_STATE_SEM_EXPANSAO.'
                 % (sum(1 for c in sem_expansao.values()
                        if c['S'] >= 2 and len(c['F']) >= 2), est['GOOD'])),
        'CELLS': len(saida),
        'BY_STATE': dict(est),
        'BY_STATE_SEM_EXPANSAO': dict(Counter(
            'GOOD' if (c['S'] >= 2 and len(c['F']) >= 2)
            else ('WEAK' if c['S'] >= 1 else 'NONE')
            for c in sem_expansao.values())),
        'SENSORES_SEM_ESPECIALIDADE_DECLARADA': sum(
            1 for s in reg['SENSORS'] if s['TIER'] in ('A', 'B') and not s['ISSUE_IDS']),
        'BY_CROP': {k: dict(v) for k, v in sorted(por_crop.items())},
        'BY_REGION': {k: dict(v) for k, v in sorted(por_regiao.items())},
        'TOP_GAPS': lacunas[:10],
        'MATRIX': saida,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    with open(COVERAGE, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('células %d · %s' % (len(saida), dict(est)))
    print('-> %s' % COVERAGE)
    return corpo


# --------------------------------------------------------------- prova de persistência
def persistencia(quantos=10):
    """Reabre o registro DO DISCO e relê sensores campo a campo.

    A prova não é "o arquivo existe". É: os campos que a missão exige sobreviveram à
    gravação e voltam legíveis, com o mesmo SENSOR_ID que a regra derivou. Um registro
    que grava e não reabre é indistinguível de um que nunca gravou.
    """
    with open(REGISTRY, encoding='utf-8') as f:
        reg = json.load(f)
    obrigatorios = list(_vazio().keys())
    escolhidos = ([s for s in reg['SENSORS'] if s['TIER'] == 'A'][:6] +
                  [s for s in reg['SENSORS'] if s['TIER'] == 'B'][:2] +
                  [s for s in reg['SENSORS'] if s['TIER'] == 'C'][:2])
    escolhidos = escolhidos[:quantos]
    provas, faltas = [], Counter()
    for s in escolhidos:
        ausentes = [k for k in obrigatorios if k not in s]
        for k in ausentes:
            faltas[k] += 1
        # o id é DERIVADO: recalcular do zero tem de devolver o mesmo valor
        if s['ENTITY_KIND'] == 'PERSON' and s['DISCOVERED_FROM'] == 'SENSOR-HUMANO-IT/EPMC':
            recalc = _sid('PERSON', '%s|%s' % (s['PERSON_NAME'], s['ORGANIZATION']))
        elif s['DISCOVERED_FROM'] == 'SENSOR-HUMANO-IT/INSTITUTIONS':
            recalc = _sid('ORGANIZATION', s['ORGANIZATION'])
        else:
            recalc = None
        provas.append({
            'SENSOR_ID': s['SENSOR_ID'],
            'ID_RECOMPUTED': recalc,
            'ID_STABLE': (recalc is None) or (recalc == s['SENSOR_ID']),
            'ENTITY_KIND': s['ENTITY_KIND'],
            'NAME': s['PERSON_NAME'] if s['ENTITY_KIND'] == 'PERSON' else s['ORGANIZATION'],
            'ROLE': s['ROLE'], 'ORGANIZATION': s['ORGANIZATION'],
            'REGION_IDS': s['REGION_IDS'], 'CROP_IDS': s['CROP_IDS'],
            'ISSUE_IDS': s['ISSUE_IDS'], 'TIER': s['TIER'],
            'MONITORING_RECOMMENDATION': s['MONITORING_RECOMMENDATION'],
            'OBSERVATION_CAPABILITIES': s['OBSERVATION_CAPABILITIES'],
            'FIELD_PROXIMITY': s['FIELD_PROXIMITY'],
            'TECHNICAL_AUTHORITY': s['TECHNICAL_AUTHORITY'],
            'LAST_CONTENT_DATE': s['LAST_CONTENT_DATE'],
            'PROVENANCE_SOURCE_ID': (s['PROVENANCE'] or {}).get('SOURCE_ID'),
            'FIELDS_PRESENT': len(obrigatorios) - len(ausentes),
            'FIELDS_REQUIRED': len(obrigatorios),
            'FIELDS_MISSING': ausentes,
        })
    ok = all(p['ID_STABLE'] for p in provas) and not faltas
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/PERSISTENCE-PROOF',
        'source': 'releitura do próprio REGISTRY.json a partir do disco',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'REGISTRY_PATH': os.path.relpath(REGISTRY, ROOT),
        'REGISTRY_BYTES': os.path.getsize(REGISTRY),
        'SENSORS_IN_FILE': len(reg['SENSORS']),
        'REOPENED': len(provas),
        'REQUIRED_FIELDS': len(obrigatorios),
        'MISSING_FIELD_COUNTS': dict(faltas),
        'ALL_IDS_STABLE': all(p['ID_STABLE'] for p in provas),
        'STATE': 'PROVED' if ok else 'FAILED_WITH_REASON',
        'SENSORS_REOPENED': provas,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    p = os.path.join(DEST, 'PERSISTENCE-PROOF.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    for x in provas:
        print('%-14s %-9s %-34s %-2s %-11s %s' % (
            x['SENSOR_ID'], 'ID_STABLE' if x['ID_STABLE'] else 'ID_DRIFT',
            (x['NAME'] or '')[:34], x['TIER'], x['MONITORING_RECOMMENDATION'],
            '%d/%d campos' % (x['FIELDS_PRESENT'], x['FIELDS_REQUIRED'])))
    print('\n%s · %d sensores reabertos -> %s' % (corpo['STATE'], len(provas), p))
    return corpo


def resumo():
    with open(REGISTRY, encoding='utf-8') as f:
        d = json.load(f)
    print('descobertos %d · qualificados %d · rejeitados %d' % (
        d['DISCOVERED'], d['QUALIFIED'], d['REJECTED']))
    print('tier %s' % d['BY_TIER'])
    print('tipo %s' % d['BY_TYPE'])
    print('região %s' % dict(list(d['BY_REGION'].items())[:10]))
    print('monitoramento %s' % d['BY_MONITORING'])


# ------------------------------------------------------------------- os 20 primários
def primarios(n=20):
    """TOP 20 PRIMARY SENSORS — seleção por COBERTURA, não por mérito.

    Isto não é um ranking e a distinção é a razão de existir da função. `REGRA-DE-COLETA
    §6` proíbe authority score, e um "top 20 dos melhores" seria exatamente isso com
    outro nome. O critério aqui é operacional:

        se eu só pudesse escutar 20 origens continuamente,
        quais 20 cobrem o maior número de células CROP x REGION x SPECIALTY da matriz
        ADAMA, sem repetir família de origem?

    Guloso sobre a cobertura, uma família de origem por vez. Trocar a ordem de leitura do
    registro não muda o conjunto, porque o desempate é pelo id, não pela posição.
    """
    with open(REGISTRY, encoding='utf-8') as f:
        reg = json.load(f)
    with open(COVERAGE, encoding='utf-8') as f:
        cov = json.load(f)

    celulas = {(c['CROP'], c['REGION'], c['SPECIALTY']) for c in cov['MATRIX']}
    por_sensor = defaultdict(set)
    for c in cov['MATRIX']:
        for s in c['SENSORS']:
            por_sensor[s['SENSOR_ID']].add((c['CROP'], c['REGION'], c['SPECIALTY']))

    idx = {s['SENSOR_ID']: s for s in reg['SENSORS']}
    escolhidos, cobertas, familias = [], set(), set()
    while len(escolhidos) < n:
        melhor, ganho_max = None, 0
        for sid, cels in sorted(por_sensor.items()):          # ordem estável pelo id
            s = idx.get(sid)
            if s is None or sid in {e['SENSOR_ID'] for e in escolhidos}:
                continue
            if s['INDEPENDENCE_GROUP'] in familias:
                continue                                       # uma família por vez
            ganho = len(cels - cobertas)
            if ganho > ganho_max:
                melhor, ganho_max = sid, ganho
        if melhor is None:
            break
        s = idx[melhor]
        cobertas |= por_sensor[melhor]
        familias.add(s['INDEPENDENCE_GROUP'])
        escolhidos.append({
            'SENSOR_ID': s['SENSOR_ID'], 'ENTITY_KIND': s['ENTITY_KIND'],
            'NAME': s['PERSON_NAME'] if s['ENTITY_KIND'] == 'PERSON' else s['ORGANIZATION'],
            'ROLE': s['ROLE'], 'ORGANIZATION': s['ORGANIZATION'],
            'REGION': s['REGION_IDS'], 'CROPS': s['CROP_IDS'],
            'TARGETS_SPECIALTIES': s['ISSUE_IDS'] or s['SPECIALTIES'],
            'WHY_ADAMA_CARES': s['ADAMA_RELEVANCE_REASON'],
            'CHANNELS': {'INSTITUTION_URL': s['INSTITUTION_URL'],
                         'YOUTUBE': s['YOUTUBE'], 'LINKEDIN': s['LINKEDIN'],
                         'INSTAGRAM': s['INSTAGRAM'],
                         'PUBLICATIONS_URL': s['PUBLICATIONS_URL']},
            'LAST_ACTIVE': s['LAST_CONTENT_DATE'],
            'MONITORING_RECOMMENDATION': s['MONITORING_RECOMMENDATION'],
            'TIER': s['TIER'],
            'OBSERVATION_CAPABILITIES': s['OBSERVATION_CAPABILITIES'],
            'CELLS_COVERED': ganho_max,
            'SELECTION_BASIS': 'cobertura marginal de células CROP x REGION x SPECIALTY, '
                               'uma família de origem por vez — não é mérito nem alcance',
        })

    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/TOP-20-PRIMARY',
        'source': 'derivado de REGISTRY.json x COVERAGE.json',
        'EVIDENCE_CLASS': 'DERIVED_SELECTION',
        'O_QUE_ISTO_NAO_E': 'não é ranking de importância, não lê AUDIENCE_SIZE e não '
                            'ordena pessoas por produtividade',
        'RULE': 'guloso por cobertura marginal, uma família de origem por sensor',
        'CELLS_TOTAL': len(celulas),
        'CELLS_COVERED_BY_TOP': len(cobertas),
        'CELLS_COVERAGE_SHARE': round(100.0 * len(cobertas) / max(1, len(celulas)), 1),
        'ORIGIN_FAMILIES_USED': len(familias),
        'SENSORS': escolhidos,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    p = os.path.join(DEST, 'TOP-20-PRIMARY.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    for i, s in enumerate(escolhidos, 1):
        print('%2d %-13s %-2s %-34s %-11s %-26s %s' % (
            i, s['SENSOR_ID'], s['TIER'], (s['NAME'] or '')[:34],
            s['MONITORING_RECOMMENDATION'], (s['ORGANIZATION'] or '')[:26],
            '+%d células' % s['CELLS_COVERED']))
    print('\n%d sensores cobrem %d das %d células (%.1f%%) -> %s' % (
        len(escolhidos), len(cobertas), len(celulas),
        corpo['CELLS_COVERAGE_SHARE'], p))
    return corpo


if __name__ == '__main__':
    {'montar': montar, 'cobertura': cobertura, 'persistencia': persistencia,
     'primarios': primarios,
     'resumo': resumo}[sys.argv[1] if len(sys.argv) > 1 else 'resumo']()
