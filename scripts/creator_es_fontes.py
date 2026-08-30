#!/usr/bin/env python3
"""
FONTES-MÃE ESPANHOLAS (§5) — AgroInfluye e BASF #YoSoyAgricultor.

    python3 scripts/creator_es_fontes.py

POR QUE ESTAS DUAS PRIMEIRO
-----------------------------
Porque são as únicas fontes espanholas que entregam, no mesmo documento,
**pessoa + handle + cultura + marca**. Uma lista de creators sem cultura obriga
a validar um a um; um prêmio com categorias POR CULTURA já vem recortado, e é
por isso que ele rende mais por consulta que qualquer varredura de hashtag.

O QUE O PRÊMIO PROVA ALÉM DOS NOMES
-------------------------------------
AgroInfluye 2026: 13 categorias, 5 nomeados cada, **66 nomeados**, mais de um
milhão de impressões e cerca de 200 mil votos do público. E **sete
patrocinadores nomeados**, dos quais **dois são empresas de proteção de
cultivo**.

Isso responde a uma pergunta que nenhuma contagem de seguidores responderia:
o ecossistema de creators agrícolas espanhol **já é comprado** por empresas de
insumo — e as de defensivo estão entre as compradoras. Mas o que elas compram é
**categoria de prêmio**, não peça de produto. `BRAND_ECOSYSTEM_SPONSORSHIP` e
`PRODUCT_ACTIVATION_PROVED` continuam sendo coisas diferentes.

O LIMITE DESTA RODADA, DECLARADO
----------------------------------
Os 66 nomeados NÃO foram extraídos: as páginas do prêmio não foram abertas
(egresso bloqueado). O que entra aqui são os nomes que o buscador nomeou
explicitamente. `HUB_YIELD` mede exatamente isso — quantos nomes uma porta
rendeu **até agora**, não quantos ela tem.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'

# ── AgroInfluye 2026 · o que a fonte nomeou explicitamente
AGROINFLUYE = dict(
  edicao='II (2026)', data='2026-03-03',
  local='Cartuja Center CITE, Sevilha',
  organizadores=['Agromillora', 'Dos Esferas Comunicación'],
  escala={'CATEGORIAS': 13, 'NOMEADOS': 66, 'NOMEADOS_POR_CATEGORIA': 5,
          'PRESENCIAIS': '+300', 'IMPRESSOES': '+1.000.000',
          'VOTOS_DO_PUBLICO': '~200.000'},
  url='https://premiosagroinfluye.com/categorias/',
  patrocinadores=[
    dict(marca='Seipasa', categoria='Tomatito', cultura='TOMATE',
         tipo_de_marca='CROP_PROTECTION_COMPANY', categoria_produto='BIOCONTROL',
         url='https://seipasa.com/en/news/seipasa-at-the-agroinfluye-2026-awards/'),
    dict(marca='Syngenta', categoria='Embajador del AOVE', cultura='OLIVO',
         tipo_de_marca='CROP_PROTECTION_COMPANY', categoria_produto='INSTITUTIONAL_SECTOR',
         url='https://premiosagroinfluye.com/categorias/'),
    dict(marca='Kuhn Ibérica', categoria='Espiga Dorada', cultura='CEREAIS',
         tipo_de_marca='MACHINERY_COMPANY', categoria_produto='MACHINERY',
         url='https://premiosagroinfluye.com/categorias/'),
    dict(marca='FENDT', categoria='Maquinaria agrícola', cultura=cr.NAO_SEI,
         tipo_de_marca='MACHINERY_COMPANY', categoria_produto='MACHINERY',
         url='https://premiosagroinfluye.com/categorias/'),
    dict(marca='DEUTZ FAHR', categoria='Promoción del consumo del vino y cultivo de la vid',
         cultura='VIDE', tipo_de_marca='MACHINERY_COMPANY', categoria_produto='MACHINERY',
         url='https://premiosagroinfluye.com/categorias/'),
    dict(marca='ZOETIS', categoria='Profesionales del sector ganadero', cultura='PECUARIA',
         tipo_de_marca='ANIMAL_HEALTH_COMPANY', categoria_produto='OTHER',
         url='https://premiosagroinfluye.com/categorias/'),
    dict(marca='ANAGAN', categoria='Cultivos leñosos: frutal, frutos secos, berries',
         cultura='LENHOSOS', tipo_de_marca=cr.NAO_SEI, categoria_produto=cr.NAO_SEI,
         url='https://premiosagroinfluye.com/categorias/'),
  ],
  premiados=[
    dict(nome='Lucía Casal', handle='@luciiaacasal', categoria='Maquineros',
         cultura=cr.NAO_SEI, nota='DUPLA: venceu Maquineros E Mejor Content Creator Agro'),
    dict(nome='Laura Domínguez', handle='@laura.agrodg', categoria='Espiga Dorada',
         cultura='CEREAIS', nota='categoria patrocinada por Kuhn Ibérica'),
    dict(nome='Sergio Rodríguez', handle='@nitofrutadyverduras', categoria='Tomatito',
         cultura='TOMATE', nota='categoria patrocinada por Seipasa'),
    dict(nome='Paula de Prado', handle='@pauladeprado',
         categoria='Mejor Content Creator (I edição)', cultura=cr.NAO_SEI, nota=''),
  ])

# ── BASF #YoSoyAgricultor · os parceiros nomeados pelo release da PRÓPRIA BASF
BASF = dict(
  campanha='#YoSoyAgricultor', ano='2020-02', marca='BASF Agro',
  tipo_de_marca='CROP_PROTECTION_COMPANY',
  formato='concurso de fotografia para agricultores; influencers como parceiros e jurados',
  url='https://www.basf.com/basf/www/es/es/media/Noticias/Noticias2020/basf-agro-lanza--yosoyagricultor--el-concurso-de-fotografia-dest',
  creators=[
    dict(nome='Lorena Guerra', handle='@agricola_lorew'),
    dict(nome='Irmãos Tribaldos', handle='@twinsfarmblog2'),
    dict(nome='Miriam Delgado', handle='@jovenes_agricultoras'),
    dict(nome='Angel Caralt', handle='@angelocromatto'),
    dict(nome='Carlos Águila', handle='@Carlos7alella'),
    dict(nome='José Antonio Arcos e Ana Rubio', handle='@khalatea'),
  ])

# ── seeds do dono (§11 do briefing anterior): CANDIDATOS, nada validado
SEEDS_ES = [
    ('Pilar Pascual', '@agripilar'),
    ('Guillermo Asín', '@agro_blog86'),
    ('Lander de Bevere', '@elguardiandelatierra'),
    ('Lucía Morales', '@agrofamily_moralesperez'),
    ('Twins Farm', '@twinsfarm'),
    ('Lucía Casal', '@luciiaacasal'),
]


def _cand(nome, handle, rota, url, cultura=cr.NAO_SEI, nota=''):
    r = cr.registro_vazio()
    r.update({
        'CREATOR_ID': 'ES-CAND-%s' % handle.lstrip('@').lower()[:24],
        'ORIGIN_ID': handle, 'NAME': nome, 'DISPLAY_NAME': handle,
        'COUNTRY': 'ES', 'LANGUAGE': 'es', 'ENTITY_KIND': 'NOT_KNOWN',
        'INSTAGRAM': handle, 'PLATFORMS': ['INSTAGRAM'],
        'HANDLE_EXISTS': 'NOT_TESTED', 'NAME_MATCH': 'NOT_TESTED',
        'PROFILE_URL': cr.NAO_SEI,
        'IDENTITY_STATE': 'NOT_PROVED',
        'IDENTITY_EVIDENCE': 'nome e handle nomeados por %s; perfil NÃO aberto' % rota,
        'CREATOR_TYPE': cr.NAO_SEI,
        'ACTUAL_FARMER': 'NOT_KNOWN', 'ACTUAL_FARMER_EVIDENCE': 'não testado',
        'FARMER_CREATOR_ROLE': 'NOT_KNOWN', 'ACTIVATION_CREATOR': 'NOT_KNOWN',
        'TECHNICAL_SENSOR_CANDIDATE': 'NOT_KNOWN', 'FIELD_VOICE_SOURCE': 'NOT_KNOWN',
        'SENSOR_ROLE_LINK': 'NOT_LINKED',
        'CROP_CLAIMED_BY_SEED': cultura,
        'CROPS': cr.NAO_SEI, 'CROP_STATE': 'NOT_KNOWN',
        'CROP_EVIDENCE': ('categoria do prêmio sugere %s — categoria NÃO é conteúdo'
                          % cultura) if cultura != cr.NAO_SEI else 'não testado',
        'CROP_PROOF_URLS': [url],
        'WINE_RELEVANCE': 'NOT_KNOWN', 'VITICULTURE_RELEVANCE': 'NOT_KNOWN',
        'OLIVE_OIL_RELEVANCE': 'NOT_KNOWN', 'OLIVE_GROWING_RELEVANCE': 'NOT_KNOWN',
        'ACTIVITY_STATE': 'NOT_MEASURED', 'AUDIENCE_TYPE': 'NOT_KNOWN',
        'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN', 'BRAND_RELATION_TYPE': 'NOT_KNOWN',
        'ADAMA_COLLABORATION_OBSERVED': 'NOT_TESTED',
        'SOURCE_URL': url, 'SOURCE_KIND': 'MASTER_SOURCE_NAMED',
        'SOURCE_ID': MISSION, 'CAPTURE_DATE': CAPTURA,
        'COLLECTION_ROUTE': 'WEB_SEARCH sobre fonte-mãe',
        'DISCOVERY_ROUTES': [rota],
        'RELEVANCE_STATE': 'RESEARCH_NEEDED',
    })
    if nota:
        r['WHY_RELEVANT'] = [nota]
    return r


def montar():
    cands, vistos = [], {}
    for p in AGROINFLUYE['premiados']:
        c = _cand(p['nome'], p['handle'], 'AGROINFLUYE_2026', AGROINFLUYE['url'],
                  p['cultura'], p['nota'])
        vistos[p['handle'].lower()] = c
        cands.append(c)
    for p in BASF['creators']:
        h = p['handle'].lower()
        if h in vistos:
            vistos[h]['DISCOVERY_ROUTES'].append('BASF_YOSOYAGRICULTOR')
            continue
        c = _cand(p['nome'], p['handle'], 'BASF_YOSOYAGRICULTOR', BASF['url'],
                  nota='parceiro nomeado no release da própria BASF Agro')
        # A relação com a marca É conhecida aqui — e é de TIPO, não de força.
        c['BRAND_RELATIONSHIP_STATE'] = 'BRAND_COLLABORATION_PROVED'
        c['BRAND_RELATION_TYPE'] = 'BRAND_COLLABORATION_PROVED'
        vistos[h] = c
        cands.append(c)
    for nome, handle in SEEDS_ES:
        h = handle.lower()
        if h in vistos:
            # §21 — a mesma pessoa em duas portas é UMA pessoa com duas rotas.
            vistos[h]['DISCOVERY_ROUTES'].append('SEED_DO_DONO_ES')
            continue
        c = _cand(nome, handle, 'SEED_DO_DONO_ES', 'SEED_EXTERNO')
        vistos[h] = c
        cands.append(c)

    for c in cands:
        faltas = cr.checar(c)
        if faltas:
            print('PORTAO %s: %s' % (c['CREATOR_ID'], faltas)); raise SystemExit(1)

    # §8 — rendimento por porta. Mede o que a porta rendeu ATE AGORA.
    from collections import Counter
    rendimento = Counter()
    for c in cands:
        for rota in c['DISCOVERY_ROUTES']:
            rendimento[rota] += 1

    duplas = [{'HANDLE': c['ORIGIN_ID'], 'ROTAS': c['DISCOVERY_ROUTES']}
              for c in cands if len(c['DISCOVERY_ROUTES']) > 1]

    cp = [p for p in AGROINFLUYE['patrocinadores']
          if p['tipo_de_marca'] == 'CROP_PROTECTION_COMPANY']

    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'LAW': 'Categoria de prêmio NÃO é conteúdo: ganhar "Tomatito" sugere tomate, '
               'não prova. CROP_STATE continua NOT_KNOWN até o conteúdo dizer.',
        'AGROINFLUYE': AGROINFLUYE,
        'BASF_YOSOYAGRICULTOR': BASF,
        'CANDIDATES': cands,
        'CANDIDATE_COUNT': len(cands),
        'HUB_YIELD_NAMES_SO_FAR': dict(rendimento),
        'MULTIPLE_DISCOVERY_ROUTES': duplas,
        'DEDUPE_NOTE': '§21 — mesma pessoa em duas portas é UMA pessoa com duas rotas '
                       'de descoberta, nunca dois creators.',
        'SPONSOR_FINDING':
            '%d dos %d patrocinadores nomeados do AgroInfluye são empresas de proteção '
            'de cultivo (%s). O ecossistema espanhol de creators já é comprado por '
            'empresas de insumo — mas o que se compra é CATEGORIA DE PRÊMIO '
            '(BRAND_ECOSYSTEM_SPONSORSHIP), não peça de produto.'
            % (len(cp), len(AGROINFLUYE['patrocinadores']),
               ', '.join(p['marca'] for p in cp)),
        'NOT_EXTRACTED': 'Os 66 nomeados NÃO foram extraídos — as páginas do prêmio não '
                         'foram abertas (egresso bloqueado). HUB_YIELD mede o que a '
                         'porta rendeu até agora, não o que ela tem.',
    }
    with open(os.path.join(cr.BASE, 'ES-MASTER-SOURCES.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/ES-MASTER-SOURCES.json')
    print('CANDIDATOS=%d  DUPLICADOS_POR_ROTA=%d' % (len(cands), len(duplas)))
    print('RENDIMENTO POR PORTA:', dict(rendimento))
    print(corpo['SPONSOR_FINDING'][:150])


if __name__ == '__main__':
    montar()
