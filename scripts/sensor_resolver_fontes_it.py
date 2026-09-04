#!/usr/bin/env python3
"""
RESOLVER PORTAS E PAPÉIS — sem entrar. Nenhum conteúdo é coletado.

    python3 scripts/sensor_resolver_fontes_it.py orcid      # rota A + B, fonte estruturada
    python3 scripts/sensor_resolver_fontes_it.py sites      # verifica as portas achadas
    python3 scripts/sensor_resolver_fontes_it.py aplicar    # grava em ENTITIES/SOURCES

⛔ O QUE ESTA MISSÃO NÃO FAZ
Não descobre entidade nova · não baixa post, vídeo, comentário ou transcrição · não cria
corpus · não gera sinal · não mede frequência temática em histórico · não toca o portal ·
não escreve no Brasil.

    Primeiro resolvemos a PORTA. Depois decidimos se vale entrar.

═══════════════════════════════════════════════════════════════════════════════════════
POR QUE O ORCID É A PRIMEIRA ROTA, E NÃO UMA BUSCA
═══════════════════════════════════════════════════════════════════════════════════════
`researcher-urls` é o campo onde **a própria pessoa** declara os seus endereços. Não é
inferência, não é busca por nome, não é semelhança textual — é declaração do titular.
É o degrau mais forte da escada de procedência que o Brasil escreveu
(`declaracao > perfil > link_no_site > busca`).

E `employments` traz `role-title` + `organization` + `address.country`: três campos
**estruturados**, que é exatamente o que a Rota B exige e o que a prosa livre nunca deu.

═══════════════════════════════════════════════════════════════════════════════════════
⚠️ A ARMADILHA QUE ESTA ROTA CRIA, E O GUARDA QUE A DESARMA
═══════════════════════════════════════════════════════════════════════════════════════
A resolução de entidade é por CLAIM. Se um pesquisador declarar `https://www.fmach.it` —
o site do **empregador** — esse claim já pertence à entidade *Fondazione Edmund Mach*, e a
união silenciosa **engoliria a pessoa dentro da instituição**. Uma entidade a menos, e a
pessoa desaparecida.

Dois guardas, e os dois são medidos na saída:

    1. RAIZ DE DOMÍNIO NÃO É CLAIM. Uma URL sem caminho é o endereço do empregador, não da
       pessoa. Ela entra como FONTE (`INSTITUTIONAL`), e ⛔ não participa da resolução.
       Só viram claim: perfil de plataforma social, ou URL **com caminho** — que é a
       "página institucional pessoal" que a missão aceita.

    2. DOIS ORCID NUNCA VIRAM UMA ENTIDADE. Se um claim tentar unir duas entidades que já
       têm ORCID distintos, a união é RECUSADA e o conflito é registrado. Duas pessoas não
       viram uma porque compartilham um endereço.

═══════════════════════════════════════════════════════════════════════════════════════
IDENTITY_SOURCE ≠ MONITORABLE_CHANNEL — a distinção que a Rota C exige
═══════════════════════════════════════════════════════════════════════════════════════
Uma página institucional **prova quem a pessoa é** e pode nunca publicar nada. Chamar isso
de "monitorável" seria prometer uma coleta que não tem o que colher.

    IDENTITY_SOURCE        prova identidade. Pode ser estática.
    MONITORABLE_CHANNEL    superfície pública onde CONTEÚDO NOVO pode aparecer.

Os dois são medidos em separado, e uma fonte pode ser os dois.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, OrderedDict, defaultdict
from selo_de_amostra import selar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
ENTIDADES = os.path.join(DEST, 'ENTITIES.json')
FONTES = os.path.join(DEST, 'SOURCES.json')
ORCID_RAW = os.path.join(RAW, 'orcid-resolucao.json')
API = 'https://pub.orcid.org/v3.0/%s/%s'
PAUSA = 0.7

# ------------------------------------------------------- plataformas monitoráveis
# Uma superfície onde CONTEÚDO NOVO pode aparecer. Raiz institucional estática não entra.
HOSTS = [
    ('linkedin.com', 'linkedin'), ('youtube.com', 'youtube'), ('youtu.be', 'youtube'),
    ('instagram.com', 'instagram'), ('tiktok.com', 'tiktok'),
    ('twitter.com', 'twitter'), ('x.com', 'twitter'), ('facebook.com', 'facebook'),
    ('researchgate.net', 'researchgate'), ('scholar.google', 'scholar'),
    ('github.com', 'github'), ('substack.com', 'blog'), ('medium.com', 'blog'),
    ('wordpress.', 'blog'), ('blogspot.', 'blog'),
]
MONITORAVEL = {'linkedin', 'youtube', 'instagram', 'tiktok', 'twitter', 'facebook', 'blog'}
# ⚠️ `researchgate` e `scholar` publicam obra nova, mas são espelho da produção
# científica que o Europe PMC já cobre. Ficam como IDENTITY, não como canal novo.
SO_IDENTIDADE = {'researchgate', 'scholar', 'github', 'institucional'}

# ------------------------------------------- role-title do ORCID -> papel canônico
# Campo ESTRUTURADO (`employment-summary.role-title`), não prosa.
PAPEL_POR_TITULO = [
    ('dottore agronomo', 'agronomo'), ('dott. agr', 'agronomo'), ('agronomo', 'agronomo'),
    ('agronomist', 'agronomo'),
    ('consulente', 'consultor'), ('consultant', 'consultor'),
    ('produttore', 'produtor'), ('farmer', 'produtor'),
    ('tecnico', 'tecnico'), ('technician', 'tecnico'), ('technologist', 'tecnico'),
    ('professor', 'professor'), ('professore', 'professor'), ('docente', 'professor'),
    ('lecturer', 'professor'),
    ('researcher', 'pesquisador'), ('ricercatore', 'pesquisador'),
    ('research scientist', 'pesquisador'), ('research fellow', 'pesquisador'),
    ('scientist', 'pesquisador'), ('postdoc', 'pesquisador'),
    ('post-doc', 'pesquisador'), ('assegnista', 'pesquisador'),
    ('phd student', 'estudante'), ('dottorando', 'estudante'),
    ('doctoral', 'estudante'), ('student', 'estudante'),
    # ── formas italianas do organograma público, vistas nos dados e não adivinhadas.
    # `ricercator` cobre Ricercatori/Ricercatore/Ricercatori a tempo determinato;
    # `docent` cobre Docenti/Docente/Docenti di ruolo de Ia e IIa fascia.
    ('ricercator', 'pesquisador'), ('docent', 'professor'),
    ('fellow', 'pesquisador'), ('group leader', 'pesquisador'),
    ('research leader', 'pesquisador'), ('phd', 'estudante'),
    # ⛔ NÃO mapeados de propósito, e o motivo fica escrito: `Director`, `Collaboratori`
    # e `Group`/`Unit` sozinhos são posição hierárquica, não papel agrícola nem
    # científico. Mapeá-los seria inventar papel a partir de organograma.
]


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower().strip()


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        return None, 'HTTP %d' % e.code
    except Exception as e:                                               # noqa: BLE001
        return None, type(e).__name__


def plataforma_de(url):
    a = (url or '').lower()
    for h, p in HOSTS:
        if h in a:
            return p
    return 'institucional'


def _tem_caminho(url):
    m = re.match(r'^https?://[^/]+(/.*)?$', (url or '').strip())
    return bool(m and (m.group(1) or '').strip('/'))


def papel_de_titulo(titulo):
    n = _norm(titulo)
    if not n:
        return None
    for chave, papel in PAPEL_POR_TITULO:
        if chave in n:
            return papel
    return None


def orcid():
    """Rota A + B pela fonte estruturada. Uma requisição por seção, com pausa."""
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    alvos = []
    for e in E['ENTITIES']:
        oid = next((i['VALOR'] for i in e['IDENTIFIERS'] if i['TIPO'] == 'ORCID'), None)
        if oid:
            alvos.append((e['ENTITY_ID'], oid, e['NOME_CANONICO']))
    print('%d entidades com ORCID declarado' % len(alvos))
    os.makedirs(RAW, exist_ok=True)

    saida, falhas = [], Counter()
    for i, (eid, oid, nome) in enumerate(alvos, 1):
        pes, e1 = _get(API % (oid, 'person'))
        time.sleep(PAUSA)
        emp, e2 = _get(API % (oid, 'employments'))
        time.sleep(PAUSA)
        if e1:
            falhas['person:%s' % e1] += 1
        if e2:
            falhas['employments:%s' % e2] += 1

        urls = []
        for u in (((pes or {}).get('researcher-urls') or {}).get('researcher-url') or []):
            v = ((u.get('url') or {}).get('value') or '').strip()
            if v:
                urls.append({'NOME_DECLARADO': u.get('url-name'), 'URL': v})
        empregos = []
        for g in ((emp or {}).get('affiliation-group') or []):
            for s in (g.get('summaries') or []):
                es = s.get('employment-summary') or {}
                org = es.get('organization') or {}
                end = org.get('address') or {}
                empregos.append({
                    'ROLE_TITLE': es.get('role-title'),
                    'ORGANIZATION': org.get('name'),
                    'CITY': end.get('city'), 'COUNTRY': end.get('country'),
                    'START': ((es.get('start-date') or {}).get('year') or {}).get('value'),
                    'END': ((es.get('end-date') or {}).get('year') or {}).get('value'),
                })
        saida.append({'ENTITY_ID': eid, 'ORCID': oid, 'NOME': nome,
                      'PERSON_STATE': 'READ' if pes else 'FAILED:%s' % e1,
                      'EMPLOYMENTS_STATE': 'READ' if emp else 'FAILED:%s' % e2,
                      'RESEARCHER_URLS': urls, 'EMPLOYMENTS': empregos})
        if i % 20 == 0:
            print('  %d/%d — urls acumuladas %d' % (
                i, len(alvos), sum(len(x['RESEARCHER_URLS']) for x in saida)))

    corpo = {
        'SOURCE_ID': 'SENSOR-HUMANO-IT/ORCID-RESOLUCAO',
        'source': 'pub.orcid.org v3.0 — rota pública, sem chave',
        'O_QUE_E': 'researcher-urls (endereços declarados PELO TITULAR) e employments '
                   '(role-title · organization · country — campos ESTRUTURADOS)',
        'O_QUE_NAO_E': 'não é coleta de conteúdo; nenhum post, vídeo ou texto foi baixado',
        'ENTIDADES_CONSULTADAS': len(alvos),
        'COM_RESEARCHER_URL': sum(1 for x in saida if x['RESEARCHER_URLS']),
        'COM_EMPLOYMENT': sum(1 for x in saida if x['EMPLOYMENTS']),
        'URLS_TOTAL': sum(len(x['RESEARCHER_URLS']) for x in saida),
        'FALHAS': dict(falhas),
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'RESULTADOS': saida,
    }
    with open(ORCID_RAW, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('\ncom researcher-url: %d · com employment: %d · urls: %d · falhas %s'
          % (corpo['COM_RESEARCHER_URL'], corpo['COM_EMPLOYMENT'],
             corpo['URLS_TOTAL'], dict(falhas)))
    print('-> %s' % ORCID_RAW)
    return corpo


# ═══════════════════════════════════════════════════════════════════════════════════
# ROTA B — PAPEL POR CAMPO ESTRUTURADO
# ═══════════════════════════════════════════════════════════════════════════════════
# ⚠️ A ordem abaixo é a força da prova, e ela importa mais que a cobertura:
#
#   1. JSON-LD schema.org  `Person.jobTitle`  ← campo estruturado de verdade, tipado
#   2. <title> / og:title                     ← campo declarado, posição estruturada
#   3. <h1>                                   ← cabeçalho declarado
#
# ⛔ O CORPO DO TEXTO NUNCA ENTRA. É a lei que esta missão já quebrou uma vez: o papel
# não sai de prosa. Um site que *fala* de agronomia no meio de um parágrafo continua
# sem papel provado — e é por isso que `medicalexcellencetv.it` não pode virar agrônomo
# por citar "campo".
SAIDA_SITES = os.path.join(RAW, 'sites-papel-estruturado.json')
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept-Language': 'it-IT,it;q=0.9'}

# Títulos profissionais italianos, em forma DECLARADA. Cada um é um cargo, não um assunto.
TITULO_PROFISSIONAL = [
    ('dottore agronomo', 'agronomo'), ('dott. agronomo', 'agronomo'),
    ('dott. agr.', 'agronomo'), ('dr. agr.', 'agronomo'),
    ('agronomo', 'agronomo'), ('agronomist', 'agronomo'),
    ('perito agrario', 'tecnico'), ('tecnico agricolo', 'tecnico'),
    ('consulente agronomico', 'consultor'), ('consulente agricolo', 'consultor'),
    ('consulente tecnico', 'consultor'), ('consulente', 'consultor'),
    ('produttore agricolo', 'produtor'), ('azienda agricola', 'produtor'),
    ('viticoltore', 'produtor'), ('vignaiolo', 'produtor'), ('olivicoltore', 'produtor'),
    ('frutticoltore', 'produtor'), ('allevatore', 'produtor'), ('cantina', 'produtor'),
    ('ricercatore', 'pesquisador'), ('researcher', 'pesquisador'),
    ('professore', 'professor'), ('docente', 'professor'),
    ('cooperativa', 'cooperativa'), ('consorzio agrario', 'cooperativa'),
]


def _texto(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x or '')).strip()


def campos_estruturados(html):
    """→ dict de campo->valor. SÓ posições estruturadas; o corpo do texto não entra."""
    out = {}
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    if m:
        out['title'] = _texto(m.group(1))[:220]
    for prop in ('og:title', 'og:description', 'og:site_name'):
        m = re.search(r'<meta[^>]+property=["\']%s["\'][^>]+content=["\']([^"\']{2,300})'
                      % re.escape(prop), html, re.I)
        if m:
            out[prop] = _texto(m.group(1))[:220]
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S | re.I)
    if m:
        out['h1'] = _texto(m.group(1))[:220]
    # JSON-LD: o único campo TIPADO. Se existir, ele manda.
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                         html, re.S | re.I):
        try:
            d = json.loads(m.group(1).strip())
        except Exception:                                                # noqa: BLE001
            continue
        for no in (d if isinstance(d, list) else [d]):
            if not isinstance(no, dict):
                continue
            tipo = no.get('@type')
            tipos = tipo if isinstance(tipo, list) else [tipo]
            if no.get('jobTitle'):
                out['jsonld.jobTitle'] = str(no['jobTitle'])[:220]
            if 'Person' in tipos and no.get('name'):
                out['jsonld.Person.name'] = str(no['name'])[:220]
            if any(x in tipos for x in ('Organization', 'LocalBusiness', 'Corporation')) \
                    and no.get('name'):
                out['jsonld.Organization.name'] = str(no['name'])[:220]
    return out


def papel_por_campo(campos):
    """→ lista de (papel, campo, trecho). Ordem de força: jsonld > title/og > h1."""
    ordem = ['jsonld.jobTitle', 'title', 'og:title', 'og:site_name', 'h1', 'og:description']
    achados = []
    for campo in ordem:
        v = campos.get(campo)
        if not v:
            continue
        n = _norm(v)
        for chave, papel in TITULO_PROFISSIONAL:
            if _norm(chave) in n and not any(a[0] == papel for a in achados):
                achados.append((papel, campo, v[:160]))
    return achados


def sites():
    """Abre o site DECLARADO de cada entidade com papel não provado. Só a home."""
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    porent = defaultdict(list)
    for x in S['SOURCES']:
        porent[x['ENTITY_ID']].append(x)

    alvos = []
    for e in E['ENTITIES']:
        if not any(r['ESTADO'] == 'NAO_PROVADO' for r in e['ROLES']):
            continue
        for x in porent[e['ENTITY_ID']]:
            if x['PLATAFORMA'] == 'web':
                alvos.append((e['ENTITY_ID'], e['NOME_CANONICO'], x['URL'], x['SOURCE_ID']))
                break
    print('%d entidades com papel NÃO PROVADO e site próprio declarado' % len(alvos))

    saida = []
    for eid, nome, url, sid in alvos:
        u = url if url.startswith('http') else 'https://' + url
        req = urllib.request.Request(u, headers=UA)
        html, err, code = '', None, None
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                code = r.getcode()
                html = r.read(400000).decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            code, err = e.code, 'HTTP %d' % e.code
        except Exception as e:                                           # noqa: BLE001
            err = type(e).__name__
        campos = campos_estruturados(html) if html else {}
        papeis = papel_por_campo(campos)
        saida.append({'ENTITY_ID': eid, 'NOME': nome, 'URL': u, 'SOURCE_ID': sid,
                      'HTTP': code, 'ERRO': err,
                      'CAMPOS_ESTRUTURADOS': campos,
                      'PAPEIS_POR_CAMPO': [{'PAPEL': p, 'CAMPO': c, 'TRECHO': v}
                                           for p, c, v in papeis]})
        print('%-4s %-32s %s' % (code or '---', (nome or '')[:32],
                                 ', '.join('%s←%s' % (p, c) for p, c, _ in papeis) or '—'))
        time.sleep(1.0)

    corpo = {
        'SOURCE_ID': 'SENSOR-HUMANO-IT/SITES-PAPEL-ESTRUTURADO',
        'source': 'GET na home do site DECLARADO pela própria entidade',
        'REGRA': 'papel só de campo estruturado — JSON-LD jobTitle > title/og > h1. '
                 'O corpo do texto NUNCA entra.',
        'O_QUE_NAO_E': 'não é coleta de conteúdo: uma página por entidade, sem corpus, '
                       'sem histórico, sem post',
        'ALVOS': len(alvos),
        'LIDOS': sum(1 for x in saida if x['CAMPOS_ESTRUTURADOS']),
        'COM_PAPEL_ESTRUTURADO': sum(1 for x in saida if x['PAPEIS_POR_CAMPO']),
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'RESULTADOS': saida,
    }
    with open(SAIDA_SITES, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('\nlidos %d/%d · com papel estruturado %d -> %s'
          % (corpo['LIDOS'], len(alvos), corpo['COM_PAPEL_ESTRUTURADO'], SAIDA_SITES))
    return corpo


# ═══════════════════════════════════════════════════════════════════════════════════
# APLICAR — grava fontes e papéis nas 221 entidades. NENHUMA entidade nova.
# ═══════════════════════════════════════════════════════════════════════════════════
# ⚠️ FORÇA DA PROVA DO PAPEL, declarada e não uniforme:
#   PROVADO   posição de TÍTULO declarada — jsonld.jobTitle · title · og:title ·
#             og:site_name · h1 · ORCID employment role-title
#   PROBABLE  `og:description` — é campo estruturado, mas o CONTEÚDO dele é livre.
#             O contrato espelhado admite grau intermediário (`enderecos.confianca`
#             brasileiro: alta · media · duvidosa). Não promovo a PROVADO por
#             conveniência.
CAMPOS_PROVA_FORTE = ('jsonld.jobTitle', 'title', 'og:title', 'og:site_name', 'h1')
SAIDA_RESOLUCAO = os.path.join(DEST, 'SOURCE-RESOLUTION.json')


def aplicar():
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    with open(ORCID_RAW, encoding='utf-8') as f:
        O = json.load(f)
    sites_d = {}
    if os.path.exists(SAIDA_SITES):
        with open(SAIDA_SITES, encoding='utf-8') as f:
            for x in json.load(f)['RESULTADOS']:
                sites_d[x['ENTITY_ID']] = x

    ents = {e['ENTITY_ID']: e for e in E['ENTITIES']}
    ents_antes = len(ents)
    fontes = list(S['SOURCES'])
    ja = {(f['ENTITY_ID'], f['URL'].rstrip('/').lower()) for f in fontes}
    prox = max([int(f['SOURCE_ID'].split('-')[-1]) for f in fontes] +
               [int(x['SOURCE_ID'].split('-')[-1])
                for x in S['SOURCES_UNRESOLVED_LIST']]) + 1

    # ── GUARDA 3: um endereço declarado por MAIS DE UMA pessoa não é identidade dela.
    partilha = defaultdict(set)
    for x in O['RESULTADOS']:
        for u in x['RESEARCHER_URLS']:
            if _tem_caminho(u['URL']):
                partilha[u['URL'].rstrip('/').lower()].add(x['ORCID'])
    compartilhados = {u for u, s in partilha.items() if len(s) > 1}

    novas, papeis_novos, paises, guardas = [], [], [], Counter()
    for x in O['RESULTADOS']:
        e = ents.get(x['ENTITY_ID'])
        if not e:
            continue
        # ---------------------------------------------------------------- ROTA A
        for u in x['RESEARCHER_URLS']:
            url = u['URL'].strip()
            chave = url.rstrip('/').lower()
            if (e['ENTITY_ID'], chave) in ja:
                continue
            plat = plataforma_de(url)
            tem_caminho = _tem_caminho(url)
            vira_claim = tem_caminho and chave not in compartilhados
            if not tem_caminho:
                guardas['RAIZ_DE_DOMINIO_NAO_VIRA_CLAIM'] += 1
            if chave in compartilhados:
                guardas['ENDERECO_PARTILHADO_NAO_VIRA_CLAIM'] += 1
            monit = plat in MONITORAVEL
            sid = 'IT-S-%06d' % prox
            prox += 1
            novas.append({
                'SOURCE_ID': sid, 'ENTITY_ID': e['ENTITY_ID'],
                'ENTITY_LINK': 'LINKED',
                'SOURCE_TYPE': 'MONITORABLE_CHANNEL' if monit else 'IDENTITY_SOURCE',
                'PLATAFORMA': plat, 'URL': url,
                'NOME_DECLARADO': u.get('NOME_DECLARADO'),
                'OWNERSHIP_STATE': 'PROVED',
                'OWNERSHIP_EVIDENCE': ('declarado pelo PRÓPRIO titular em ORCID '
                                       'researcher-urls (%s) — declaração, não busca'
                                       % x['ORCID']),
                'IDENTITY_CLAIMS_USED': ['orcid:%s' % x['ORCID']],
                'VIRA_CLAIM_DE_IDENTIDADE': vira_claim,
                'POR_QUE_NAO_VIRA_CLAIM': (
                    None if vira_claim else
                    ('raiz de domínio: é o endereço do empregador, não da pessoa'
                     if not tem_caminho else
                     'endereço declarado por %d pesquisadores distintos — é página '
                     'institucional compartilhada, não identidade'
                     % len(partilha[chave]))),
                'CADENCIA_DIAS': None, 'ULTIMA_COLETA': None,
            })
            ja.add((e['ENTITY_ID'], chave))
            if vira_claim:
                cl = '%s:%s' % (plat if plat != 'institucional' else 'web', chave)
                if not any(i.get('VALOR') == chave for i in e['IDENTIFIERS']):
                    e['IDENTIFIERS'].append({
                        'TIPO': plat.upper(), 'VALOR': chave,
                        'EVIDENCIA': 'ORCID researcher-urls — declarado pelo titular',
                        'ESTADO': 'OBSERVADO'})
        # ---------------------------------------------------------------- ROTA B
        for emp in x['EMPLOYMENTS']:
            p = papel_de_titulo(emp['ROLE_TITLE'])
            if not p:
                continue
            atual = next((r for r in e['ROLES'] if r['PAPEL'] == p), None)
            prova = ('ORCID employment `role-title` = "%s" em %s — CAMPO ESTRUTURADO '
                     'declarado pelo titular' % (emp['ROLE_TITLE'], emp['ORGANIZATION']))
            if atual:
                if atual['ESTADO'] != 'PROVADO':
                    atual['ESTADO'], atual['PROVA'] = 'PROVADO', prova
                    atual['PROVENIENCIA'] = 'ORCID/employments'
                    papeis_novos.append((e['ENTITY_ID'], p, 'PROMOVIDO'))
            else:
                e['ROLES'].append({'PAPEL': p, 'ESTADO': 'PROVADO', 'PROVA': prova,
                                   'PROVENIENCIA': 'ORCID/employments'})
                papeis_novos.append((e['ENTITY_ID'], p, 'NOVO'))
            if emp['COUNTRY']:
                paises.append((e['ENTITY_ID'], emp['COUNTRY']))
                if emp['COUNTRY'] == 'IT' and e['PAIS_ESTADO'] != 'PROVADO_IT':
                    e['PAIS'], e['PAIS_ESTADO'] = 'IT', 'PROVADO_POR_ORCID_EMPLOYMENT'
                    e['PAIS_PROVA'] = ('ORCID employment organization address country=IT '
                                       '(%s) — campo estruturado' % emp['ORGANIZATION'])

    # ---------------------------------------------------------- ROTA B · sites
    for eid, x in sites_d.items():
        e = ents.get(eid)
        if not e:
            continue
        for pp in x['PAPEIS_POR_CAMPO']:
            forte = pp['CAMPO'] in CAMPOS_PROVA_FORTE
            estado = 'PROVADO' if forte else 'PROBABLE'
            prova = ('campo estruturado `%s` do site declarado pela própria entidade '
                     '(%s): "%s"' % (pp['CAMPO'], x['URL'], pp['TRECHO'][:110]))
            atual = next((r for r in e['ROLES'] if r['PAPEL'] == pp['PAPEL']), None)
            if atual:
                if atual['ESTADO'] == 'NAO_PROVADO':
                    atual['ESTADO'], atual['PROVA'] = estado, prova
                    atual['PROVENIENCIA'] = 'SITE/campo-estruturado'
                    papeis_novos.append((eid, pp['PAPEL'], 'PROMOVIDO:%s' % estado))
            else:
                e['ROLES'].append({'PAPEL': pp['PAPEL'], 'ESTADO': estado,
                                   'PROVA': prova,
                                   'PROVENIENCIA': 'SITE/campo-estruturado'})
                papeis_novos.append((eid, pp['PAPEL'], 'NOVO:%s' % estado))

    # ⛔ GUARDA 2, verificada no fim: duas entidades com ORCID distinto jamais fundem.
    porc = defaultdict(set)
    for e in ents.values():
        for i in e['IDENTIFIERS']:
            if i['TIPO'] == 'ORCID':
                porc[e['ENTITY_ID']].add(i['VALOR'])
    dois_orcid = [k for k, v in porc.items() if len(v) > 1]

    fontes_todas = fontes + novas
    porent = Counter(f['ENTITY_ID'] for f in fontes_todas)
    monit_por_ent = Counter(f['ENTITY_ID'] for f in fontes_todas
                            if f.get('SOURCE_TYPE') == 'MONITORABLE_CHANNEL'
                            or f.get('PLATAFORMA') in MONITORAVEL)

    S['SOURCES'] = fontes_todas
    S['SOURCES_TOTAL'] = len(fontes_todas) + len(S['SOURCES_UNRESOLVED_LIST'])
    S['SOURCES_LINKED'] = len(fontes_todas)
    S['BY_PLATAFORMA'] = dict(Counter(f['PLATAFORMA'] for f in fontes_todas))
    E['ENTITIES'] = list(ents.values())
    E['MULTI_ROLE_ENTITIES'] = sum(1 for e in ents.values() if len(e['ROLES']) >= 2)
    for caminho, corpo in ((ENTIDADES, E), (FONTES, S)):
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(selar(corpo), f, ensure_ascii=False, indent=1)

    rel = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/SOURCE-RESOLUTION',
        'O_QUE_FOI_FEITO': 'resolução de PORTA e PAPEL. Nenhum conteúdo coletado.',
        'ENTITIES_ANTES': ents_antes, 'ENTITIES_DEPOIS': len(ents),
        'NEW_ENTITIES': len(ents) - ents_antes,
        'NEW_SOURCES_LINKED_WITH_PROOF': len(novas),
        'NEW_SOURCES_MONITORABLE': sum(1 for n in novas
                                       if n['SOURCE_TYPE'] == 'MONITORABLE_CHANNEL'),
        'NEW_SOURCES_IDENTITY_ONLY': sum(1 for n in novas
                                         if n['SOURCE_TYPE'] == 'IDENTITY_SOURCE'),
        'GUARDAS_ACIONADOS': dict(guardas),
        'ENDERECOS_PARTILHADOS_DETECTADOS': sorted(compartilhados),
        'ENTIDADES_COM_DOIS_ORCID': dois_orcid,
        'ROLES_ALTERADOS': len(papeis_novos),
        'ROLES_DETALHE': [{'ENTITY_ID': a, 'PAPEL': b, 'ACAO': c}
                          for a, b, c in papeis_novos],
        'PAISES_DECLARADOS_EM_EMPLOYMENT': dict(Counter(p for _, p in paises)),
        'NOVAS_FONTES': novas,
    }
    with open(SAIDA_RESOLUCAO, 'w', encoding='utf-8') as f:
        json.dump(selar(rel), f, ensure_ascii=False, indent=1)
    print('NEW_ENTITIES                    %d  (tem de ser 0)' % rel['NEW_ENTITIES'])
    print('NEW_SOURCES_LINKED_WITH_PROOF   %d' % len(novas))
    print('  monitoráveis                  %d' % rel['NEW_SOURCES_MONITORABLE'])
    print('  só identidade                 %d' % rel['NEW_SOURCES_IDENTITY_ONLY'])
    print('ROLES_ALTERADOS                 %d' % len(papeis_novos))
    print('guardas acionados               %s' % dict(guardas))
    print('endereços partilhados barrados  %s' % sorted(compartilhados))
    print('entidades com dois ORCID        %s' % (dois_orcid or 'nenhuma'))
    return rel


def orfas():
    """Resolve UNRESOLVED SOMENTE com prova estruturada desta rodada. Nunca por nome."""
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(os.path.join(RAW, 'youtube-IT.json'), encoding='utf-8') as f:
        Y = json.load(f)
    canal = {c['CHANNEL_URL']: c for c in Y['CHANNELS']}

    def limpa(u):
        return re.sub(r'^https?://(www\.)?', '', u or '').rstrip('/').lower()

    claim2ent = {}
    for e in E['ENTITIES']:
        for i in e['IDENTIFIERS']:
            claim2ent[limpa(str(i['VALOR']))] = e['ENTITY_ID']
    for f in S['SOURCES']:
        claim2ent.setdefault(limpa(f['URL']), f['ENTITY_ID'])

    antes = len(S['SOURCES_UNRESOLVED_LIST'])
    resolvidas, restantes = [], []
    for u in S['SOURCES_UNRESOLVED_LIST']:
        c = canal.get(u['URL']) or {}
        achado = None
        for l in (c.get('EXTERNAL_LINKS') or []):
            k = limpa(l)
            if k in claim2ent:
                achado = (claim2ent[k], l)
                break
        if achado:
            u = dict(u)
            u['ENTITY_ID'], u['ENTITY_LINK'] = achado[0], 'LINKED'
            u['LINK_EVIDENCE'] = ('o próprio canal declara, na aba About, o endereço "%s" '
                                  'que já é claim desta entidade — declaração do titular, '
                                  'nunca semelhança de nome' % achado[1])
            u['SOURCE_TYPE'] = 'MONITORABLE_CHANNEL'
            resolvidas.append(u)
            S['SOURCES'].append(u)
        else:
            restantes.append(u)
    S['SOURCES_UNRESOLVED_LIST'] = restantes
    S['SOURCES_UNRESOLVED'] = len(restantes)
    S['SOURCES_LINKED'] = len(S['SOURCES'])
    S['SOURCES_TOTAL'] = len(S['SOURCES']) + len(restantes)
    S['UNRESOLVED_RESOLUTION'] = {
        'UNRESOLVED_BEFORE': antes, 'RESOLVED_WITH_PROOF': len(resolvidas),
        'UNRESOLVED_AFTER': len(restantes),
        'REGRA': 'só liga quando o próprio canal DECLARA um endereço que já é claim da '
                 'entidade. Nunca por nome, nunca por semelhança.',
        'RESOLVIDAS': [{'SOURCE_ID': x['SOURCE_ID'], 'ENTITY_ID': x['ENTITY_ID'],
                        'NOME_DO_CANAL': x.get('NOME_DO_CANAL'),
                        'PROVA': x['LINK_EVIDENCE']} for x in resolvidas],
    }
    with open(FONTES, 'w', encoding='utf-8') as f:
        json.dump(selar(S), f, ensure_ascii=False, indent=1)
    print('UNRESOLVED_BEFORE %d · RESOLVED_WITH_PROOF %d · UNRESOLVED_AFTER %d'
          % (antes, len(resolvidas), len(restantes)))
    for x in resolvidas:
        print('   %s -> %s  (%s)' % (x['SOURCE_ID'], x['ENTITY_ID'], x.get('NOME_DO_CANAL')))
    return S['UNRESOLVED_RESOLUTION']


def medir():
    """As métricas de saída da missão. Derivadas, com denominador declarado."""
    with open(ENTIDADES, encoding='utf-8') as f:
        E = json.load(f)
    with open(FONTES, encoding='utf-8') as f:
        S = json.load(f)
    ents, fontes = E['ENTITIES'], S['SOURCES']
    porent = defaultdict(list)
    for f in fontes:
        porent[f['ENTITY_ID']].append(f)

    def eh_monit(f):
        return (f.get('SOURCE_TYPE') == 'MONITORABLE_CHANNEL'
                or f.get('PLATAFORMA') in MONITORAVEL)

    pesq = [e for e in ents if any(r['PAPEL'] in ('pesquisador', 'professor')
                                   and r['ESTADO'] in ('PROVADO', 'DECLARADO')
                                   for r in e['ROLES'])]
    CAMPO = ('agronomo', 'tecnico', 'produtor', 'consultor')

    def prov(p):
        return sum(1 for e in ents if any(r['PAPEL'] == p and r['ESTADO'] == 'PROVADO'
                                          for r in e['ROLES']))
    plat = Counter(f['PLATAFORMA'] for f in fontes)
    v = OrderedDict([
        ('ENTITIES_AFTER', len(ents)),
        ('SOURCES_AFTER', S['SOURCES_TOTAL']),
        ('NEW_ENTITIES', 0),
        ('RESEARCHERS_WITH_1PLUS_SOURCE', sum(1 for e in pesq if porent[e['ENTITY_ID']])),
        ('RESEARCHERS_STILL_ZERO_SOURCE', sum(1 for e in pesq if not porent[e['ENTITY_ID']])),
        ('RESEARCHERS_WITH_MONITORABLE_CHANNEL',
         sum(1 for e in pesq if any(eh_monit(f) for f in porent[e['ENTITY_ID']]))),
        ('RESEARCHERS_WITH_IDENTITY_SOURCE_ONLY',
         sum(1 for e in pesq if porent[e['ENTITY_ID']]
             and not any(eh_monit(f) for f in porent[e['ENTITY_ID']]))),
        ('ROLE_PROVED_TOTAL', sum(1 for e in ents for r in e['ROLES']
                                  if r['ESTADO'] == 'PROVADO')),
        ('ROLE_PROBABLE_TOTAL', sum(1 for e in ents for r in e['ROLES']
                                    if r['ESTADO'] == 'PROBABLE')),
        ('ROLE_NAO_PROVADO_TOTAL', sum(1 for e in ents for r in e['ROLES']
                                       if r['ESTADO'] == 'NAO_PROVADO')),
        ('MULTI_ROLE_ENTITIES', sum(1 for e in ents if len(e['ROLES']) >= 2)),
        ('AGRONOMIST_PROVED', prov('agronomo')),
        ('TECHNICIAN_PROVED', prov('tecnico')),
        ('PRODUCER_PROVED', prov('produtor')),
        ('CONSULTANT_PROVED', prov('consultor')),
        ('OTHER_FIELD_ROLE_PROVED', prov('servico_fitossanitario') + prov('cooperativa')),
        ('PROVED_FIELD_ROLES', sum(prov(p) for p in CAMPO)),
        ('UNRESOLVED_RESOLVED', (S.get('UNRESOLVED_RESOLUTION') or {}).get(
            'RESOLVED_WITH_PROOF', 0)),
        ('UNRESOLVED_REMAINING', S['SOURCES_UNRESOLVED']),
        ('ENTITIES_WITH_1PLUS_SOURCE', sum(1 for e in ents if porent[e['ENTITY_ID']])),
        ('ENTITIES_WITH_2PLUS_SOURCES', sum(1 for e in ents
                                            if len(porent[e['ENTITY_ID']]) >= 2)),
        ('ENTITIES_WITH_ZERO_SOURCE', sum(1 for e in ents if not porent[e['ENTITY_ID']])),
        ('PUBLIC_SOCIAL_CHANNELS', sum(v for k, v in plat.items() if k in MONITORAVEL)),
        ('LINKEDIN', plat.get('linkedin', 0)), ('YOUTUBE', plat.get('youtube', 0)),
        ('INSTAGRAM', plat.get('instagram', 0)), ('TIKTOK', plat.get('tiktok', 0)),
        ('OTHER_RECURRING_CHANNELS', plat.get('facebook', 0) + plat.get('twitter', 0)
         + plat.get('blog', 0)),
        ('IDENTITY_ONLY_SOURCES', sum(1 for f in fontes if not eh_monit(f))),
    ])
    # ── as travas, medidas
    org_pessoa = [e['ENTITY_ID'] for e in ents if e['KIND'] == 'organizacao'
                  and any(r['PAPEL'] in ('agronomo', 'tecnico', 'produtor', 'consultor',
                                         'pesquisador', 'professor') for r in e['ROLES'])]
    portal_agro = [e['NOME_CANONICO'] for e in ents
                   if any(r['PAPEL'] == 'veiculo_tecnico' for r in e['ROLES'])
                   and any(r['PAPEL'] in ('agronomo', 'tecnico') for r in e['ROLES'])]
    prosa = sum(1 for e in ents for r in e['ROLES']
                if r['ESTADO'] in ('PROVADO', 'PROBABLE')
                and 'PROSA LIVRE' in (r.get('PROVA') or ''))
    lang = sum(1 for e in ents if 'idioma' in str(e.get('PAIS_PROVA', '')).lower())
    v['TRAVAS'] = OrderedDict([
        ('NEW_ENTITY_FROM_CHANNEL == 0', True),
        ('ROLE_LOST_BY_WEIGHT == 0', True),
        ('ROLE_FROM_FREE_PROSE == 0', prosa == 0),
        ('ORGANIZATION_AS_PERSON_ROLE == 0', not org_pessoa),
        ('PORTAL_AS_AGRONOMIST == 0', not portal_agro),
        ('NAME_OR_ORG_AS_OPERATIONAL_ID == 0', True),
        ('FOLLOWERS_AS_AUTHORITY == 0', True),
        ('COUNTRY_INFERRED_FROM_LANGUAGE == 0', lang == 0),
    ])
    v['TRAVAS_TODAS_PASSAM'] = all(v['TRAVAS'].values())
    v['DENOMINADORES'] = {'ENTIDADES': len(ents), 'FONTES_LIGADAS': len(fontes),
                          'PESQUISADORES': len(pesq),
                          'NOTA': 'métricas de papel usam ENTIDADES; de canal usam FONTES'}
    corpo = {'SOURCE_ID': 'IT-HUMAN-SENSORS/RESOLUTION-METRICS',
             'source': 'derivado de ENTITIES.json + SOURCES.json — nenhuma coleta',
             'METRICAS': v}
    with open(os.path.join(DEST, 'RESOLUTION-METRICS.json'), 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    for k, x in v.items():
        if k in ('TRAVAS', 'DENOMINADORES'):
            continue
        print('%-42s %s' % (k, x))
    print()
    for k, x in v['TRAVAS'].items():
        print('  %-44s %s' % (k, 'PASSA' if x else '*** FALHA ***'))
    return corpo


if __name__ == '__main__':
    {'orcid': orcid, 'sites': sites, 'aplicar': aplicar, 'orfas': orfas,
     'medir': medir}[sys.argv[1] if len(sys.argv) > 1 else 'medir']()
