#!/usr/bin/env python3
"""
FICHA RICA DE ORIGEM — abrir um SENSOR_ID e responder as 15 perguntas.

    python3 scripts/sensor_ficha.py fichas
    python3 scripts/sensor_ficha.py hibridos

A ficha é montada no CONTRATO BRASILEIRO (entidade · fonte · documento), não na
taxonomia italiana. Toda afirmação carrega a sua prova; sem prova, sai `NÃO SEI`.

⚠️ A DIFERENÇA ENTRE ENRIQUECER E INVENTAR
--------------------------------------------
Enriquecer é ler o que já foi coletado e organizá-lo no contrato. Nenhum campo desta
ficha é preenchido por dedução: se o canal não foi encontrado, `CANAIS = []`, e não
"provavelmente tem Instagram".

⚠️ PAPÉIS SÃO MULTIVALORADOS, E CADA UM CARREGA A SUA PROVA
-------------------------------------------------------------
O modelo italiano gravava UM `SENSOR_TYPE`. A realidade não é exclusiva: um agrônomo
com canal é agrônomo E tem presença pública. Aqui os papéis vêm em lista, cada um com
`PROVA`, e `PRESENCA_PUBLICA` é uma dimensão à parte — nunca um papel profissional.

    ⛔ ROLE = creator          — o que o modelo italiano faria
    ✅ papeis = [agronomo]     + presenca_publica = [youtube]

Isto obedece a lei brasileira de que `papel_da_fonte` descreve **o que a conta é para a
entidade** (company · person · marca · canal_tecnico · veiculo), e nunca a profissão.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from selo_de_amostra import selar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
REGISTRY = os.path.join(DEST, 'REGISTRY.json')
MAPA = os.path.join(DEST, 'MAPA-BRASIL.json')
SAIDA = os.path.join(DEST, 'FICHAS.json')

# Papel profissional (o que a pessoa/org É) — separado de presença pública (onde fala).
PAPEL_PROFISSIONAL = {
    'RESEARCHER': 'pesquisador', 'PLANT_PATHOLOGIST': 'pesquisador',
    'ENTOMOLOGIST': 'pesquisador', 'RESEARCH_ORGANIZATION': 'organizacao_de_pesquisa',
    'PUBLIC_RESEARCH': 'organizacao_de_pesquisa', 'UNIVERSITY': 'organizacao_de_pesquisa',
    'RESEARCH_CENTRE': 'organizacao_de_pesquisa', 'TRIAL_CENTRE': 'centro_de_ensaio',
    'PLANT_HEALTH_SERVICE': 'servico_fitossanitario',
    'PHYTOSANITARY_CONSORTIUM': 'servico_fitossanitario',
    'AGRONOMIST': 'agronomo', 'TECHNICAL_ADVISER': 'consultor',
    'FIELD_TECHNICIAN': 'tecnico', 'CROP_PROTECTION': 'tecnico',
    'DECISION_SUPPORT_SERVICE': 'servico_tecnico',
    'PRODUCER': 'produtor', 'VITICULTURE': 'produtor', 'FRUIT_GROWING': 'produtor',
    'OLIVE_GROWING': 'produtor', 'WINERY': 'produtor', 'NURSERY': 'produtor',
    'COOPERATIVE': 'cooperativa', 'PRODUCER_ORGANIZATION': 'organizacao_de_produtores',
    'AGRICULTURAL_CONSORTIUM': 'cooperativa', 'CONSORTIUM': 'cooperativa',
    'FARMER_ASSOCIATION': 'associacao', 'TECHNICAL_MEDIA': 'veiculo_tecnico',
    'FOOD_INDUSTRY': 'empresa', 'VETERINARY_PUBLIC_HEALTH': 'orgao_publico',
}


def _papeis(s):
    """→ lista de {papel, prova}. Multivalorado, cada um com a sua prova."""
    st = s['SENSOR_TYPE']
    brutos = (st.split(':', 1)[1].split('|') if st.startswith('AMBIGUOUS:') else [st])
    out, vistos = [], set()
    for b in brutos:
        p = PAPEL_PROFISSIONAL.get(b)
        if not p or p in vistos:
            continue
        vistos.add(p)
        out.append({'PAPEL': p, 'PROVA': s['ROLE_BASIS'],
                    'ORIGEM_DA_PROVA': s['DISCOVERED_FROM']})
    # ⚠️ O papel científico só é afirmado quando há obra em escopo anexada — cargo não
    # basta, e a missão proíbe presumir capacidade pelo cargo.
    if s['DISCOVERED_FROM'].endswith('/EPMC') and s['OBSERVATION_EVIDENCE']:
        if 'pesquisador' not in vistos:
            out.append({'PAPEL': 'pesquisador',
                        'PROVA': '%d obras em escopo, ids anexados'
                                 % ((s['PROVENANCE'] or {}).get('WORKS_IN_SCOPE') or 0),
                        'ORIGEM_DA_PROVA': s['DISCOVERED_FROM']})
    return out


def _ficha(s, fontes_por_sensor):
    fs = fontes_por_sensor.get(s['SENSOR_ID'], [])
    social = [f for f in fs if f['plataforma'] in ('youtube', 'instagram', 'linkedin')]
    prov = s['PROVENANCE'] or {}
    return {
        'SENSOR_ID': s['SENSOR_ID'],
        'QUEM_E': {
            'nome_canonico': (s['PERSON_NAME'] if s['ENTITY_KIND'] == 'PERSON'
                              else s['ORGANIZATION']) if not str(
                                  s['ORGANIZATION']).startswith('NÃO SEI')
                             else prov.get('CHANNEL_NAME', 'NÃO SEI'),
            'entidade_tipo_br': None,   # preenchido pelo chamador a partir do MAPA
            'pessoa_ou_organizacao': s['ENTITY_KIND'],
            'organizacao_ligada': s['ORGANIZATION'],
            'identificadores': {
                'ORCID': prov.get('ORCID_DECLARED') or 'NÃO SEI',
                'ORCID_ESTADO': prov.get('ORCID_STATE') or 'NÃO SEI',
                'external_ids': ['%s:%s' % (f['plataforma'], f['external_id']) for f in fs],
            },
            'evidencia_de_identidade': s['TECHNICAL_AUTHORITY_BASIS'],
            'dono_canonico': s['CANONICAL_OWNER'],
        },
        'O_QUE_FAZ': {'papeis': _papeis(s), 'papeis_count': len(_papeis(s))},
        'POR_QUE_ESTA_NO_SINTONIA': s['ADAMA_RELEVANCE_REASON'],
        'ONDE_ATUA': {
            'pais': s['COUNTRY'],
            'regiao': s['REGION_IDS'] or ['NÃO SEI'],
            'base_da_regiao': s['REGION_BASIS'],
            'onde_mora': 'NÃO SEI — nunca foi coletado',
            'onde_trabalha': (s['REGION_IDS'] or ['NÃO SEI'])[0],
            'onde_produz': 'NÃO SEI — nunca foi coletado',
            'sobre_onde_fala': 'NÃO SEI — exige conteúdo coletado',
        },
        'CULTURAS': {'lista': s['CROP_IDS'],
                     'prova': 'herdadas da CONSULTA que trouxe a origem, nunca do título'},
        'PROBLEMAS': {'lista': s['ISSUE_IDS'] or s['SPECIALTIES'],
                      'prova': s['OBSERVATION_CAPABILITIES_BASIS']},
        'RELACAO_COM_O_CAMPO': {
            'proximidade': s['FIELD_PROXIMITY'], 'prova': s['FIELD_PROXIMITY_BASIS']},
        'RELACAO_COM_A_CIENCIA': {
            'autoridade_cientifica': ('DECLARADA' if s['AUTHORITY_CLASS'] == 'SCIENCE'
                                      else 'NÃO SEI'),
            'obras_em_escopo': prov.get('WORKS_IN_SCOPE', 'NÃO SEI'),
            'evidencia': s['OBSERVATION_EVIDENCE'][:2]},
        'CANAIS_PUBLICOS': [{
            'plataforma': f['plataforma'], 'external_id': f['external_id'],
            'url': f['url'], 'papel_da_fonte': f['papel_da_fonte'],
            'prova_de_pertencimento': ('declarado na própria página/aba About da origem'
                                       if f['plataforma'] != 'web'
                                       else 'URL institucional verificada por GET'),
        } for f in fs],
        'PRESENCA_PUBLICA': {
            'tem_rede_social': bool(social),
            'plataformas': sorted({f['plataforma'] for f in social}),
            'NOTA': 'presença pública NÃO é papel profissional. Um agrônomo com canal '
                    'continua sendo agrônomo; "creator" nunca vira tipo de entidade.'},
        'QUANDO_FALOU_POR_ULTIMO': s['LAST_CONTENT_DATE'],
        'SOBRE_O_QUE_FALA_RECORRENTEMENTE': {
            'recorrencia_cientifica': prov.get('WORKS_IN_SCOPE', 'NÃO SEI'),
            'recorrencia_tecnica': 'NÃO SEI — exige conteúdo coletado',
            'recorrencia_social': 'NÃO SEI — exige conteúdo coletado'},
        'AUTORIDADE': {
            'cientifica': s['TECHNICAL_AUTHORITY'] if s['AUTHORITY_CLASS'] == 'SCIENCE'
                          else 'NÃO SEI',
            'tecnica': s['TECHNICAL_AUTHORITY'],
            'base': s['TECHNICAL_AUTHORITY_BASIS']},
        'ALCANCE': {'valor': s['AUDIENCE_SIZE'],
                    'NOTA': 'ALCANCE nunca é autoridade e não entra em nenhuma régua'},
        'CRUZAMENTOS_POSSIVEIS': [
            c for c in [
                'FIELD (bollettino territorial)' if s['SENSOR_TYPE'] in (
                    'PLANT_HEALTH_SERVICE', 'PHYTOSANITARY_CONSORTIUM') else None,
                'SCIENCE (obras em escopo)' if prov.get('WORKS_IN_SCOPE') else None,
                'COMPETITOR COMMUNICATION' if s['SENSOR_TYPE'] == 'TECHNICAL_MEDIA' else None,
                'CROP WINDOW (crop×target da matriz ADAMA)' if s['CROP_IDS'] else None,
            ] if c],
        'MONITORAMENTO_RECOMENDADO': s['MONITORING_RECOMMENDATION'],
        'COLETAVEL_HOJE': bool(fs) and bool(social),
        'POR_QUE_NAO_COLETAVEL': (None if (fs and social) else
                                  ('nenhum canal público resolvido' if not fs else
                                   'só tem endereço web institucional, sem conta de '
                                   'plataforma — a coleta de conteúdo não tem onde bater')),
    }


def fichas():
    with open(REGISTRY, encoding='utf-8') as f:
        reg = json.load(f)
    with open(MAPA, encoding='utf-8') as f:
        mapa = json.load(f)
    fps = defaultdict(list)
    for x in mapa['FONTES']:
        fps[x['SENSOR_ID_ITALIANO']].append(x)
    tipo_ent = {}
    for e in mapa['ENTIDADES']:
        for sid in e['SENSOR_IDS']:
            tipo_ent[sid] = e['tipo']

    S = reg['SENSORS']
    def pega(f, n):
        return [s for s in S if f(s)][:n]

    grupos = {
        'PESQUISADORES': pega(lambda s: s['SENSOR_TYPE'] == 'RESEARCHER' and s['TIER'] == 'A', 3),
        'TECNICOS_AGRONOMICOS': pega(
            lambda s: s['SENSOR_TYPE'] in ('PLANT_HEALTH_SERVICE', 'FIELD_TECHNICIAN',
                                           'TECHNICAL_ADVISER', 'DECISION_SUPPORT_SERVICE'), 3),
        'PRODUTORES': pega(lambda s: s['SENSOR_TYPE'] in (
            'PRODUCER', 'WINERY', 'VITICULTURE', 'OLIVE_GROWING'), 3),
        'COOPERATIVAS_ORGANIZACOES': pega(lambda s: s['SENSOR_TYPE'] in (
            'COOPERATIVE', 'PRODUCER_ORGANIZATION', 'AGRICULTURAL_CONSORTIUM'), 3),
        'COM_PRESENCA_SOCIAL': pega(
            lambda s: any(f['plataforma'] in ('youtube', 'instagram', 'linkedin')
                          for f in fps.get(s['SENSOR_ID'], [])), 3),
    }
    out = {}
    for g, ss in grupos.items():
        out[g] = []
        for s in ss:
            fi = _ficha(s, fps)
            fi['QUEM_E']['entidade_tipo_br'] = tipo_ent.get(s['SENSOR_ID'], 'NAO_RESOLVIDA')
            out[g].append(fi)

    # ------------------------------------------------------- os casos híbridos exigidos
    def hib(cond):
        return [s['SENSOR_ID'] for s in S if cond(s)]
    social_ids = {s['SENSOR_ID'] for s in S
                  if any(f['plataforma'] in ('youtube', 'instagram', 'linkedin')
                         for f in fps.get(s['SENSOR_ID'], []))}
    hibridos = {
        'PRODUTOR_MAIS_CREATOR': hib(lambda s: PAPEL_PROFISSIONAL.get(
            s['SENSOR_TYPE'].split(':')[-1].split('|')[0]) == 'produtor'
            and s['SENSOR_ID'] in social_ids),
        'AGRONOMO_MAIS_CREATOR': hib(lambda s: 'AGRONOMIST' in s['SENSOR_TYPE']
                                     and s['SENSOR_ID'] in social_ids),
        'PESQUISADOR_MAIS_VOZ_SOCIAL': hib(lambda s: s['SENSOR_TYPE'] == 'RESEARCHER'
                                           and s['SENSOR_ID'] in social_ids),
        'ORGANIZACAO_MAIS_MULTIPLOS_CANAIS': hib(
            lambda s: len(fps.get(s['SENSOR_ID'], [])) >= 2
            and s['ENTITY_KIND'] != 'PERSON'),
    }
    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/FICHAS',
        'source': 'derivado de REGISTRY.json + MAPA-BRASIL.json — nenhuma coleta nova',
        'CONTRATO': 'entidade · fonte · documento (portal-sintonia)',
        'REGRA_DE_PAPEL': 'multivalorado, cada papel com a sua prova; PRESENCA_PUBLICA '
                          'é dimensão à parte e nunca vira papel profissional',
        'FICHAS_POR_GRUPO': {k: len(v) for k, v in out.items()},
        'CASOS_HIBRIDOS': {k: {'QUANTOS': len(v), 'SENSOR_IDS': v[:6],
                               'ESTADO': 'PRESENTE' if v else 'AUSENTE'}
                           for k, v in hibridos.items()},
        'FICHAS': out,
    }
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(selar(corpo), f, ensure_ascii=False, indent=1)
    print('fichas por grupo: %s' % corpo['FICHAS_POR_GRUPO'])
    print('\ncasos híbridos:')
    for k, v in corpo['CASOS_HIBRIDOS'].items():
        print('  %-36s %-9s %d' % (k, v['ESTADO'], v['QUANTOS']))
    print('\n-> %s' % SAIDA)
    return corpo


if __name__ == '__main__':
    {'fichas': fichas}[sys.argv[1] if len(sys.argv) > 1 else 'fichas']()
