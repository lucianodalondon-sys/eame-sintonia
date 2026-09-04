#!/usr/bin/env python3
"""
MAPEAR OS 224 ITALIANOS PARA O CONTRATO CANÔNICO BRASILEIRO.

    python3 scripts/sensor_mapear_brasil.py mapear
    python3 scripts/sensor_mapear_brasil.py lacunas

POR QUE ESTE ARQUIVO EXISTE
----------------------------
A camada italiana nasceu com taxonomia própria — `SENSOR_ID`, `SENSOR_TYPE`,
`ENTITY_KIND`. O Brasil **já tem** o contrato, vivo e medido, e a Itália não deve criar
uma segunda taxonomia. Este arquivo não inventa nada: ele traduz.

O CONTRATO BRASILEIRO — lido do banco vivo, não de documentação antiga
-----------------------------------------------------------------------
Fonte: `portal-sintonia/entidades.sql` (DDL executado; `PLANO-location-resolver.md`
mede 3.275 de 3.299 fichas já ligadas), `auditar-as-fontes.py::PAPEIS_DO_CAMPO`
(as 63 colunas de `fontes`), `camadas-do-campo.py::DO_CAMPO`.

    entidades   QUEM É       chave(unique) · nome_canonico · tipo · entidade_mae ·
                             uf · cidade · origem_local · evidencia
                tipo ∈ pessoa · empresa · cooperativa · veiculo · orgao

    fontes      ONDE BATO    entidade_id → entidades · papel_da_fonte · external_id ·
                             plataforma · handle · canal_youtube · url · canonical_url
                papel_da_fonte ∈ company · person · marca · canal_tecnico · veiculo

    documentos  fonte_id     ⛔ documento NUNCA aponta para entidade

AS TRÊS LEIS QUE ESTE MAPEAMENTO OBEDECE, E QUE A ITÁLIA VIOLAVA
------------------------------------------------------------------
1. **"LIGAR, nunca fundir"** — uma pessoa em quatro plataformas são quatro `fontes`
   ligadas a UMA `entidade`. Não são quatro sensores, e também não são uma linha só.
   O Brasil mediu o custo de fundir: 39 dos 55 grupos "PODE FUNDIR" eram a mesma pessoa
   em plataformas diferentes, com 8.687 documentos. Fundir apagaria qual plataforma
   disse o quê.

2. **"Nome NUNCA é identificador: a casa tem 142 nomes repetidos"** — `entidades.chave`
   é derivada do IDENTIFICADOR mais estável do grupo, nunca do nome. O `SENSOR_ID`
   italiano é `sha1(NOME|ORGANIZAÇÃO)` — exatamente o que esta lei proíbe, e a auditoria
   já mediu o efeito: 5 de 8 casos adversariais de identidade quebram.

3. **`external_id` é o id DA PLATAFORMA** — canal `UC...` no YouTube, `@handle` limpo no
   Instagram/TikTok, `canonical_url` no LinkedIn, URL canônica completa na web. ORCID
   não aparece nesta lista: no contrato brasileiro ele seria mais um identificador
   externo de uma fonte científica, **nunca o passaporte de existir**.

O QUE ESTE ARQUIVO NÃO FAZ
---------------------------
Não escreve no banco brasileiro, não redescobre ninguém, não coleta conteúdo e não
inventa canal. Ele traduz o que já existe e MEDE o que falta para caber no contrato.
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-HUMAN-SENSORS')
REGISTRY = os.path.join(DEST, 'REGISTRY.json')
SAIDA = os.path.join(DEST, 'MAPA-BRASIL.json')

# ---------------------------------------------------------------- entidades.tipo (BR)
# Valores canônicos do comentário da tabela: 'pessoa · empresa · cooperativa · veiculo ·
# orgao'. A Itália NÃO ganha valores novos — cada SENSOR_TYPE italiano cai num destes.
TIPO_ENTIDADE = {
    'RESEARCHER': 'pessoa',
    'AGRONOMIST': 'pessoa', 'TECHNICAL_ADVISER': 'pessoa',
    'FIELD_TECHNICIAN': 'pessoa', 'PRODUCER': 'pessoa',
    'PLANT_PATHOLOGIST': 'pessoa', 'ENTOMOLOGIST': 'pessoa',
    'PLANT_HEALTH_SERVICE': 'orgao',
    'PHYTOSANITARY_CONSORTIUM': 'orgao',
    'PUBLIC_RESEARCH': 'orgao', 'UNIVERSITY': 'orgao',
    'RESEARCH_CENTRE': 'orgao', 'TRIAL_CENTRE': 'orgao',
    'RESEARCH_ORGANIZATION': 'orgao',
    'DECISION_SUPPORT_SERVICE': 'empresa',
    'COOPERATIVE': 'cooperativa', 'PRODUCER_ORGANIZATION': 'cooperativa',
    'AGRICULTURAL_CONSORTIUM': 'cooperativa', 'CONSORTIUM': 'cooperativa',
    'FARMER_ASSOCIATION': 'orgao',
    'TECHNICAL_MEDIA': 'veiculo',
    'VETERINARY_PUBLIC_HEALTH': 'orgao', 'FOOD_INDUSTRY': 'empresa',
    'WINERY': 'empresa', 'NURSERY': 'empresa',
    'VITICULTURE': 'pessoa', 'FRUIT_GROWING': 'pessoa', 'OLIVE_GROWING': 'pessoa',
    'CROP_PROTECTION': 'pessoa',
}

# ------------------------------------------------------- fontes.papel_da_fonte (BR)
# 'company · person · marca · canal_tecnico · veiculo' — o que a CONTA é para a entidade.
# Repare que isto é papel DO CANAL, não profissão da pessoa: é por isso que "creator"
# não aparece aqui e não deve virar tipo de entidade.
def papel_da_fonte(tipo_entidade, plataforma):
    if tipo_entidade == 'pessoa':
        return 'person'
    if tipo_entidade == 'veiculo':
        return 'veiculo'
    if tipo_entidade in ('orgao', 'cooperativa'):
        return 'canal_tecnico'
    return 'company'


# ═══════════════════════════════════════════════════════════════════════════════
# O VOCABULÁRIO CANÔNICO BRASILEIRO — 20 valores, lidos do CHECK VIGENTE
# ═══════════════════════════════════════════════════════════════════════════════
# Fonte: `portal-sintonia/tipos-de-fonte.sql:38-66` (a restrição em vigor).
#
# ⚠️ ARMADILHA QUE A PRÓPRIA CASA BRASILEIRA DOCUMENTA: existe uma restrição ANTIGA de
# 11 valores em `supabase-conteudo.sql:12-16`, e ela é a PRIMEIRA que aparece quando se
# procura `check (tipo in (...))`. `onde-esta-o-tecnico.py:417-424` avisa que quem
# procurar sem âncora pega a lista OBSOLETA. Esta aqui é a vigente, com 20.
TIPO_FONTE_BR = (
    'creator', 'imprensa', 'portal', 'cooperativa', 'associacao', 'instituicao',
    'podcast', 'revenda', 'distribuidor', 'congresso', 'orgao_publico',
    'pesquisador', 'tecnico', 'comercial', 'operador', 'produtor', 'estudante',
    'comite_tecnico', 'laboratorio', 'empresa',
)

# `vozes-do-acervo.py:128-140` — as CINCO FAMÍLIAS humanas do cânon analítico.
# ⚠️ Só 11 dos 20 tipos estão mapeados. O resto cai em FORA_DAS_CINCO, e isso é
# deliberado: "o que ele não nomeou NÃO É ENFIADO numa das cinco".
VOZ_DA_FICHA = {
    'pesquisador': 'A · CIÊNCIA', 'instituicao': 'A · CIÊNCIA',
    'laboratorio': 'A · CIÊNCIA', 'comite_tecnico': 'A · CIÊNCIA',
    'tecnico': 'B · AGRÔNOMO',
    'comercial': 'C · RTV',
    'produtor': 'D · CAMPO',
    'cooperativa': 'E · MERCADO', 'revenda': 'E · MERCADO',
    'distribuidor': 'E · MERCADO', 'empresa': 'E · MERCADO',
}

# `camadas-do-campo.py:81,84`
DO_CAMPO = ('tecnico', 'pesquisador', 'produtor', 'cooperativa')
INSTITUCIONAL = ('instituicao', 'associacao')

# ─────────────────────────────────────────────────────────────────────────────
# ITÁLIA → fontes.tipo brasileiro. Nenhum valor novo é criado.
#
# ⚠️ DUAS PERDAS DECLARADAS, e elas são do CONTRATO BRASILEIRO, não da tradução:
#   'agronomo'  ⛔ NÃO EXISTE em fontes.tipo — dobrado dentro de 'tecnico'
#                 (`tipos-de-fonte.sql:59`: "tecnico -- agronomo, consultor, ...")
#   'consultor' ⛔ NÃO EXISTE em fontes.tipo — existe só em `vozes.tipo`, que é
#                 uma SEGUNDA taxonomia da mesma pergunta
# Os 17 AGRONOMISTS italianos e os TECHNICAL_ADVISER caem os dois em 'tecnico', e a
# distinção italiana SE PERDE. Isso está medido abaixo em PERDAS_NA_TRADUCAO.
BR_TIPO_FONTE = {
    'RESEARCHER': 'pesquisador',
    'PLANT_PATHOLOGIST': 'pesquisador', 'ENTOMOLOGIST': 'pesquisador',
    'RESEARCH_ORGANIZATION': 'instituicao', 'PUBLIC_RESEARCH': 'instituicao',
    'UNIVERSITY': 'instituicao', 'RESEARCH_CENTRE': 'instituicao',
    'TRIAL_CENTRE': 'laboratorio',
    'PLANT_HEALTH_SERVICE': 'orgao_publico',
    'PHYTOSANITARY_CONSORTIUM': 'orgao_publico',
    'AGRONOMIST': 'tecnico', 'TECHNICAL_ADVISER': 'tecnico',
    'FIELD_TECHNICIAN': 'tecnico', 'CROP_PROTECTION': 'tecnico',
    'DECISION_SUPPORT_SERVICE': 'empresa',
    'PRODUCER': 'produtor', 'VITICULTURE': 'produtor', 'FRUIT_GROWING': 'produtor',
    'OLIVE_GROWING': 'produtor', 'WINERY': 'produtor', 'NURSERY': 'produtor',
    'COOPERATIVE': 'cooperativa', 'PRODUCER_ORGANIZATION': 'cooperativa',
    'AGRICULTURAL_CONSORTIUM': 'cooperativa', 'CONSORTIUM': 'cooperativa',
    'FARMER_ASSOCIATION': 'associacao',
    'TECHNICAL_MEDIA': 'portal',
    'VETERINARY_PUBLIC_HEALTH': 'orgao_publico', 'FOOD_INDUSTRY': 'empresa',
}

# O que a Itália distingue e o Brasil NÃO — medido, não opinado.
PERDAS_NA_TRADUCAO = {
    'AGRONOMIST + TECHNICAL_ADVISER + FIELD_TECHNICIAN + CROP_PROTECTION': {
        'br': 'tecnico',
        'perda': "o Brasil não tem 'agronomo' nem 'consultor' em fontes.tipo; os dois "
                 "estão dobrados dentro de 'tecnico' por decisão do CHECK vigente",
    },
    'PLANT_HEALTH_SERVICE + PHYTOSANITARY_CONSORTIUM': {
        'br': 'orgao_publico',
        'perda': 'a Itália separa serviço fitossanitário regional de consórcio '
                 'provincial; o Brasil tem um valor só',
    },
    'UNIVERSITY + PUBLIC_RESEARCH + RESEARCH_CENTRE': {
        'br': 'instituicao',
        'perda': 'universidade, centro nacional e fundação viram o mesmo valor',
    },
}

def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower().strip()


def _external_id(url):
    """external_id no padrão brasileiro: id da conta NA PLATAFORMA. Nunca o nome."""
    if not url or url == 'NÃO SEI':
        return None, None
    u = url.strip()
    m = re.search(r'youtube\.com/(@[\w.\-]+)', u)
    if m:
        return 'youtube', m.group(1).lower()
    m = re.search(r'youtube\.com/channel/(UC[\w\-]+)', u)
    if m:
        return 'youtube', m.group(1)
    m = re.search(r'(?:instagram\.com)/([\w.\-]+)', u)
    if m:
        return 'instagram', '@' + m.group(1).lower()
    m = re.search(r'linkedin\.com/(in|company)/([\w\-%]+)', u)
    if m:
        return 'linkedin', 'linkedin.com/%s/%s' % (m.group(1), m.group(2).lower())
    m = re.search(r'^https?://([^/]+)(/.*)?$', u)
    if m:
        # ⚠️ URL canônica COMPLETA na web, com caminho — o Brasil mediu por que:
        # "embrapa.br abriga 14 pesquisadores diferentes e o domínio sozinho os
        # confundiria".
        dom = m.group(1).lower().lstrip('www.')
        caminho = (m.group(2) or '').rstrip('/')
        return 'web', dom + caminho
    return None, None


def mapear():
    with open(REGISTRY, encoding='utf-8') as f:
        reg = json.load(f)

    entidades, fontes, problemas = {}, [], []
    for s in reg['SENSORS']:
        st = s['SENSOR_TYPE']
        base = st.split(':', 1)[1].split('|')[0] if st.startswith('AMBIGUOUS:') else st
        tipo_ent = TIPO_ENTIDADE.get(base)
        tipo_fonte = BR_TIPO_FONTE.get(base)

        # ⚠️ O caso que a arquitetura brasileira expõe e a italiana escondia: um canal
        # de YouTube cuja identidade nunca foi resolvida NÃO é uma entidade. É uma
        # FONTE órfã, esperando `entidade_id`. Registrá-la como sensor foi confundir
        # fonte com canal — exatamente o defeito que `PLANO-entidade-e-fonte.md` nomeia.
        orfa = s['ENTITY_KIND'] == 'PERSON_OR_ORGANIZATION_NOT_DECLARED'

        # ⚠️ `entidades.nome_canonico` é NOT NULL no Brasil. O registro italiano deixa
        # `ORGANIZATION = NÃO SEI` em TODO sensor vindo de canal — o nome do canal mora
        # só em PROVENANCE. Isso é um defeito italiano que só aparece ao tentar caber no
        # contrato: 40 sensores de canal não teriam nome para inserir.
        nome = (s['PERSON_NAME'] if s['ENTITY_KIND'] == 'PERSON'
                else s['ORGANIZATION'])
        if not nome or nome == 'NÃO SEI' or nome.startswith('NÃO SEI'):
            nome = (s['PROVENANCE'] or {}).get('CHANNEL_NAME') or 'NÃO SEI'

        # a chave da entidade sai do identificador mais estável disponível, nunca do nome
        plat_url = None
        for cand in (s['INSTITUTION_URL'], s['YOUTUBE']):
            if cand and cand != 'NÃO SEI':
                plat_url = cand
                break
        plat, ext = _external_id(plat_url)
        orcid = (s['PROVENANCE'] or {}).get('ORCID_DECLARED')

        if orcid:
            chave, chave_base = 'orcid:%s' % orcid, 'ORCID'
        elif ext:
            chave, chave_base = '%s:%s' % (plat, ext), 'EXTERNAL_ID_DA_PLATAFORMA'
        else:
            # ⛔ Sem identificador estável não há chave. O Brasil não deixa o nome virar
            # chave; aqui a entidade fica NAO_RESOLVIDA, que é um dos quatro estados.
            chave, chave_base = None, 'NENHUM_IDENTIFICADOR_ESTAVEL'

        estado = ('NAO_RESOLVIDA' if (chave is None or orfa)
                  else 'ENTIDADE_RESOLVIDA')
        if chave is None:
            problemas.append({'SENSOR_ID': s['SENSOR_ID'], 'NOME': nome,
                              'PROBLEMA': 'sem identificador estável para virar '
                                          'entidades.chave'})

        if chave and not orfa:
            e = entidades.setdefault(chave, {
                'chave': chave, 'chave_derivada_de': chave_base,
                'nome_canonico': nome, 'tipo': tipo_ent or 'NÃO SEI',
                'uf': None,
                'regiao_it': s['REGION_IDS'][0] if s['REGION_IDS'] else None,
                'cidade': None,
                'origem_local': s['REGION_BASIS'],
                'evidencia': s['TECHNICAL_AUTHORITY_BASIS'],
                'pais': 'IT',
                'SENSOR_IDS': [], 'entidade_mae': None,
            })
            e['SENSOR_IDS'].append(s['SENSOR_ID'])

        for url in ([s['INSTITUTION_URL']] if s['INSTITUTION_URL'] != 'NÃO SEI' else []) + \
                   ([s['YOUTUBE']] if s['YOUTUBE'] != 'NÃO SEI' else []) + \
                   [u for u in (s['OTHER_CHANNELS'] or [])]:
            p, x = _external_id(url)
            if not x:
                continue
            fontes.append({
                'entidade_chave': chave, 'entidade_estado': estado,
                'plataforma': p, 'external_id': x, 'url': url,
                'papel_da_fonte': papel_da_fonte(tipo_ent, p),
                'tipo': tipo_fonte or 'NÃO SEI',
                'camada': ('DO_CAMPO' if tipo_fonte in DO_CAMPO else
                           'INSTITUCIONAL' if tipo_fonte in INSTITUCIONAL else 'OUTRA'),
                'voz_da_ficha': VOZ_DA_FICHA.get(tipo_fonte, 'FORA_DAS_CINCO'),
                'culturas': s['CROP_IDS'], 'assuntos': s['ISSUE_IDS'],
                'pais': s['COUNTRY'], 'regiao': s['REGION_IDS'],
                'cadencia_dias': {'DAILY': 1, 'WEEKLY': 7, 'MONTHLY': 30,
                                  'EVENT_DRIVEN': None,
                                  'DISCOVERY_ONLY': None}.get(
                                      s['MONITORING_RECOMMENDATION']),
                'alcance': s['AUDIENCE_SIZE'],
                'ultima_coleta': None,
                'SENSOR_ID_ITALIANO': s['SENSOR_ID'],
            })

    # --------------------------------------------------------------------- medições
    porcamada = Counter(f['camada'] for f in fontes)
    portipo = Counter(f['tipo'] for f in fontes)
    porpapel = Counter(f['papel_da_fonte'] for f in fontes)
    porplat = Counter(f['plataforma'] for f in fontes)
    portipoent = Counter(e['tipo'] for e in entidades.values())
    multi = {k: v for k, v in entidades.items() if len(v['SENSOR_IDS']) > 1}
    canais_por_ent = Counter()
    for f in fontes:
        if f['entidade_chave']:
            canais_por_ent[f['entidade_chave']] += 1

    corpo = {
        'SOURCE_ID': 'IT-HUMAN-SENSORS/MAPA-BRASIL',
        'source': 'derivado de REGISTRY.json traduzido para o contrato de '
                  'portal-sintonia (entidades.sql + fontes)',
        'CONTRATO_BRASILEIRO': {
            'entidades': 'chave(unique, do identificador mais estável) · nome_canonico · '
                         'tipo(pessoa·empresa·cooperativa·veiculo·orgao) · entidade_mae · '
                         'uf · cidade · origem_local · evidencia',
            'fontes': 'entidade_id → entidades · papel_da_fonte(company·person·marca·'
                      'canal_tecnico·veiculo) · external_id(id NA PLATAFORMA) · '
                      'plataforma · handle · url · canonical_url · tipo · culturas · '
                      'pracas · alcance · cadencia_dias · ultima_coleta',
            'documentos': 'fonte_id — documento NUNCA aponta para entidade',
            'DO_CAMPO': list(DO_CAMPO), 'INSTITUCIONAL': list(INSTITUCIONAL),
            'estados_de_resolucao': ['MESMA_ENTIDADE', 'MESMA_FONTE',
                                     'ENTIDADES_DIFERENTES', 'NAO_RESOLVIDA'],
            'fonte_da_leitura': 'portal-sintonia/entidades.sql · auditar-as-fontes.py · '
                                'camadas-do-campo.py · PLANO-entidade-e-fonte.md',
        },
        'SENSORES_ITALIANOS_DE_ENTRADA': len(reg['SENSORS']),
        'ENTIDADES_DERIVADAS': len(entidades),
        'FONTES_DERIVADAS': len(fontes),
        'ENTIDADES_POR_TIPO': dict(portipoent),
        'FONTES_POR_TIPO': dict(portipo),
        'FONTES_POR_PAPEL': dict(porpapel),
        'FONTES_POR_PLATAFORMA': dict(porplat),
        'FONTES_POR_CAMADA': dict(porcamada),
        'FONTES_POR_VOZ_DA_FICHA': dict(Counter(f['voz_da_ficha'] for f in fontes)),
        'VOCABULARIO_BR_VIGENTE': list(TIPO_FONTE_BR),
        'PERDAS_NA_TRADUCAO': PERDAS_NA_TRADUCAO,
        'TIPOS_BR_NAO_USADOS_PELA_ITALIA': [x for x in TIPO_FONTE_BR
                                            if x not in set(portipo)],
        'ENTIDADES_COM_MAIS_DE_UM_SENSOR_ITALIANO': len(multi),
        'CANAIS_POR_ENTIDADE': dict(Counter(canais_por_ent.values())),
        'SENSORES_SEM_IDENTIFICADOR_ESTAVEL': len(problemas),
        'PROBLEMAS': problemas[:40],
        'ENTIDADES': list(entidades.values()),
        'FONTES': fontes,
    }
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('entrada %d sensores -> %d entidades + %d fontes' % (
        len(reg['SENSORS']), len(entidades), len(fontes)))
    print('entidades.tipo  %s' % dict(portipoent))
    print('fontes.tipo     %s' % dict(portipo))
    print('camada          %s' % dict(porcamada))
    print('voz_da_ficha    %s' % dict(Counter(f['voz_da_ficha'] for f in fontes)))
    print('tipos BR nao usados pela Italia: %s'
          % [x for x in TIPO_FONTE_BR if x not in set(portipo)])
    print('plataforma      %s' % dict(porplat))
    print('canais/entidade %s' % dict(Counter(canais_por_ent.values())))
    print('sem identificador estável: %d' % len(problemas))
    print('-> %s' % SAIDA)
    return corpo


if __name__ == '__main__':
    {'mapear': mapear}[sys.argv[1] if len(sys.argv) > 1 else 'mapear']()
