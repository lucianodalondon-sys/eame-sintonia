#!/usr/bin/env python3
"""
FILAS DE DESCOBERTA — quem entra na próxima coleta, e por quê.

A missão 10B-ES pede fila, não coleta. O ponto é justamente esse: 152 buscas às cegas
seriam volume sem critério, e o repositório já mediu o que isso custa. Aqui a seleção é
derivada do corpus e cada linha carrega o `WHY_SELECTED` que a produziu.

Os critérios, todos declarados e todos vindos do dado:

  RELEVANCE   o par CROP × ISSUE precisa tocar o problema-âncora (olivar / repilo e
              vizinhos), não agricultura em geral
  RECENCY     trabalho recente — quem parou em 2019 não é voz pública de hoje
  INSTITUTION afiliação declarada e verificável no corpus
  IDENTITY    ORCID presente
  NOT_CONFLATED  número de organizações dentro da faixa do quadro. Foi exatamente por
              aqui que a auditoria achou um id do OpenAlex que juntou homônimos
              (58 organizações contra mediana 2), e a regra virou vigia.
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')

# Problemas que tocam a âncora da rodada espanhola.
ISSUES_ANCORA = {'REPILO', 'OLIVE_DISEASE', 'OLIVE_PESTS', 'OLIVE_KNOT',
                 'XYLELLA', 'VERTICILLIUM'}
ANO_MINIMO = 2023


def _ler(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


def limiar_conflacao(pessoas):
    """Teto de organizações a partir do próprio quadro, não de número escolhido a dedo."""
    n = [len(p.get('ALL_ORGANIZATIONS') or []) for p in pessoas]
    return max(10, statistics.median(n) * 10)


def selecionar_pesquisadores(meta=20):
    pessoas = _ler('ES-RESEARCHERS-OLIVE.json')['RESEARCHERS']
    teto = limiar_conflacao(pessoas)
    fila, recusados = [], []
    for p in pessoas:
        issues = set(p.get('ISSUES') or [])
        n_org = len(p.get('ALL_ORGANIZATIONS') or [])
        motivos = []
        if 'OLIVE' not in (p.get('CROPS') or []):
            motivos.append('CROP fora da âncora')
        if not (issues & ISSUES_ANCORA):
            motivos.append('nenhum ISSUE da âncora')
        if (p.get('LAST_KNOWN_ACTIVITY') or 0) < ANO_MINIMO:
            motivos.append('sem trabalho desde %s' % p.get('LAST_KNOWN_ACTIVITY'))
        if not p.get('ORCID'):
            motivos.append('sem ORCID')
        org = p.get('ORGANIZATION')
        if not org or 'NÃO SEI' in str(org):
            motivos.append('sem instituição declarada')
        if n_org > teto:
            motivos.append('possível conflação: %d organizações (teto %g)' % (n_org, teto))
        if motivos:
            recusados.append({'NAME': p['NAME'], 'MOTIVOS': motivos})
            continue
        fila.append({
            'PERSON_ID': p['PERSON_ID'], 'NAME': p['NAME'], 'ORCID': p['ORCID'],
            'INSTITUTION': org, 'ALL_INSTITUTIONS_COUNT': n_org,
            'CROP': p.get('CROPS'), 'ISSUE': sorted(issues & ISSUES_ANCORA),
            'PUBLICATION_COUNT_IN_SCOPE': p.get('PUBLICATION_COUNT_IN_SCOPE'),
            'LAST_KNOWN_ACTIVITY': p.get('LAST_KNOWN_ACTIVITY'),
            'WHY_SELECTED': (
                '%d trabalho(s) no escopo, atividade até %s, %d tema(s) da âncora (%s), '
                'ORCID presente, instituição declarada (%s), %d organizações — dentro da '
                'faixa do quadro (teto %g)' % (
                    p.get('PUBLICATION_COUNT_IN_SCOPE'), p.get('LAST_KNOWN_ACTIVITY'),
                    len(issues & ISSUES_ANCORA), '+'.join(sorted(issues & ISSUES_ANCORA)),
                    org, n_org, teto)),
            'PUBLIC_LINKEDIN_STATUS': 'NOT_TESTED',
            'PUBLIC_YOUTUBE_STATUS': 'NOT_TESTED',
        })
    # ordenação declarada: mais temas da âncora, depois mais trabalho, depois mais recente
    fila.sort(key=lambda x: (-len(x['ISSUE']), -(x['PUBLICATION_COUNT_IN_SCOPE'] or 0),
                             -(x['LAST_KNOWN_ACTIVITY'] or 0), x['NAME']))
    return fila[:meta], fila, recusados, teto


def selecionar_vozes_tecnicas(meta=20):
    """Vozes técnicas já verificadas no LinkedIn, priorizadas por papel — nunca por alcance."""
    origens = _ler('ES-VOICE-LINKEDIN.json')['ORIGINS']
    PRIORIDADE = ['TECHNICAL_ADVISER', 'RESEARCHER', 'PUBLIC_RESEARCH_INSTITUTION',
                  'PUBLIC_AUTHORITY', 'COOPERATIVE', 'PRODUCER_ORGANISATION',
                  'EDUCATION_INSTITUTION', 'INDUSTRY_ASSOCIATION', 'TECHNICAL_MEDIA']
    TOPICO = {'OLIVE': 0, 'PLANT_HEALTH': 1, 'AGRI_GENERAL': 2}
    fila = []
    for o in origens:
        if not o.get('PUBLIC_TECHNICAL_VOICE'):
            continue
        if o['DECLARED_ROLE'] not in PRIORIDADE:
            continue
        fila.append({
            'ORIGIN_ID': o['ORIGIN_ID'], 'NAME': o['NAME'],
            'DECLARED_ROLE': o['DECLARED_ROLE'], 'ROLE_EVIDENCE': o['ROLE_EVIDENCE'],
            'ROLE_BASIS': o['ROLE_BASIS'], 'DECLARED_TOPIC': o['DECLARED_TOPIC'],
            'DECLARED_LOCATION': o['DECLARED_LOCATION'], 'REGION': o['REGION'],
            'URL': o['URL'], 'DISCOVERY_ROUTE': o['DISCOVERY_ROUTE'],
            'WHY_SELECTED': (
                'papel %s declarado em campo estruturado (%s), evidência "%s"; tópico %s '
                'declarado. Alcance NÃO entrou na seleção.' % (
                    o['DECLARED_ROLE'], o['ROLE_BASIS'], o['ROLE_EVIDENCE'],
                    o['DECLARED_TOPIC'])),
            'PUBLIC_CONTENT_STATUS': 'NOT_TESTED',
        })
    fila.sort(key=lambda x: (TOPICO.get(x['DECLARED_TOPIC'], 9),
                             PRIORIDADE.index(x['DECLARED_ROLE']), x['NAME']))
    return fila[:meta], fila


if __name__ == '__main__':
    q, todos, rec, teto = selecionar_pesquisadores()
    print('pesquisadores elegíveis: %d de 152 (teto de conflação: %g organizações)' % (len(todos), teto))
    print('na fila: %d' % len(q))
    v, tv = selecionar_vozes_tecnicas()
    print('vozes técnicas elegíveis: %d | na fila: %d' % (len(tv), len(v)))
