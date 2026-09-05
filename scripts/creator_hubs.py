#!/usr/bin/env python3
"""
DISCOVERY HUBS — universidade, feira, associação e prêmio NÃO são creators.

    python3 scripts/creator_hubs.py montar

POR QUE ISTO É UM ARQUIVO E NÃO UMA COLUNA
--------------------------------------------
Porque hub e creator respondem a perguntas diferentes. Um hub não tem
seguidores, não tem cultura provada por conteúdo e não pode ser "ativado". Ele
tem uma coisa que o creator não tem: **gente dentro**. Misturá-los num ranking
faria a ETSIAM de Córdoba competir com um agricultor por posição — e a
universidade venceria por prestígio sem nunca ter falado com um produtor no
Instagram.

O hub existe para RESPONDER: *de onde saem os próximos nomes?*

IDENTIDADE DE HUB TAMBÉM SE PROVA
-----------------------------------
Duas entradas da lista externa chegaram com identidade em aberto — e elas
entram com esse estado escrito, não maquiado:

    "IIT Agro"            não aceitar como unidade formal sem prova
    "Osservatorio Agro"   entidade não confirmada; não coletar em volume

E uma entrada chegou com correção explícita do dono: o antigo **SIMA** foi
cancelado, então ele não pode ser master discovery source sem que uma edição
efetivamente medida exista. Fica `DEMOTED` com o motivo.

`ROLE` e `PRIORITY` desta rodada são **asserção do dono da missão**, não
medição nossa. O campo `ROLE_SOURCE` diz isso em cada linha, para que ninguém
os leia daqui a um mês como se fossem resultado de pesquisa.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'
ASSERT = 'ASSERTED_BY_MISSION_OWNER — não medido por nós nesta rodada'

# (pais, nome, papéis, prioridade, foco, estado_de_identidade, nota)
HUBS = [
 # ───────────────────────────────────────────────────────────────── ESPANHA
 ('ES', 'Premios AgroInfluye', ['AWARD', 'CREATOR_DISCOVERY_HUB'], 'VERY_HIGH',
  ['MULTI_CROP'], 'PROVED',
  'MASTER CREATOR DISCOVERY SOURCE. 2ª edição em Sevilha (Cartuja Center), '
  '+300 presentes e ~1.500 por streaming. Organizado por Agromillora e Dos '
  'Esferas Comunicación. Categorias por CULTURA — e patrocinadas por empresas '
  'de insumo, o que faz deste prêmio evidência dupla: descobre creators E '
  'documenta ativação de marca.',
  'https://premiosagroinfluye.com/categorias/'),
 ('ES', 'BASF #YoSoyAgricultor', ['AWARD', 'BRAND_ACTIVATION_OBSERVER'], 'HIGH',
  ['MULTI_CROP'], 'PROVED',
  'Concurso de fotografia da BASF Agro (2020) com influencers agrícolas '
  'nomeados como parceiros. Caso histórico de empresa de crop protection '
  'usando creators na Espanha.',
  'https://www.basf.com/basf/www/es/es/media/Noticias/Noticias2020/basf-agro-lanza--yosoyagricultor--el-concurso-de-fotografia-dest'),
 ('ES', 'ETSIAM Córdoba / UCO', ['TECHNICAL_SPEAKER_HUB', 'CREATOR_DISCOVERY_HUB'],
  'VERY_HIGH', ['OLIVE', 'PLANT_PROTECTION', 'AGRONOMY', 'MACHINERY',
                'PRECISION_AGRICULTURE'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('ES', 'ETSEAMN / UPV (+ ecossistema IAM/UPV)', ['TECHNICAL_SPEAKER_HUB'], 'HIGH',
  ['CITRUS', 'HORTICULTURE', 'FRUIT', 'ENTOMOLOGY', 'PLANT_PATHOLOGY'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('ES', 'ETSIAAB / UPM', ['TECHNICAL_SPEAKER_HUB'], 'HIGH',
  ['PLANT_DISEASE', 'WEED_SCIENCE', 'BIOCONTROL', 'PHYTOSANITARY_USE',
   'HORTICULTURE'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('ES', 'Cajamar INNOVA / Est. Exp. Las Palmerillas',
  ['FARMER_NETWORK_HUB', 'TECHNICAL_SPEAKER_HUB', 'CREATOR_DISCOVERY_HUB'],
  'VERY_HIGH', ['GREENHOUSE', 'TOMATO', 'PEPPER', 'HORTICULTURE', 'PESTS',
                'DISEASES', 'WATER', 'AGTECH'], 'NOT_TESTED',
  ASSERT + ' · foco Almería', cr.NAO_SEI),
 ('ES', 'ASAJA (nacional + ASAJA Joven + regionais)',
  ['FARMER_NETWORK_HUB', 'CREATOR_DISCOVERY_HUB'], 'VERY_HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT + ' · não usar só o nacional', cr.NAO_SEI),
 ('ES', 'COAG (Juventudes Agrarias, Programa Cultiva, regionais)',
  ['FARMER_NETWORK_HUB', 'CREATOR_DISCOVERY_HUB'], 'HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('ES', 'UPA (UPA Joven + regionais)',
  ['FARMER_NETWORK_HUB', 'CREATOR_DISCOVERY_HUB'], 'VERY_HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('ES', 'AINIA', ['TECHNICAL_SPEAKER_HUB'], 'MEDIUM_LOW', ['FOOD_INNOVATION'],
  'NOT_TESTED', ASSERT + ' · não gastar volume antes dos hubs de agricultores',
  cr.NAO_SEI),
 ('ES', 'Tecnalia', ['AGTECH_SOURCE', 'TECHNICAL_SPEAKER_HUB'], 'MEDIUM',
  ['AGTECH'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('ES', 'Seipasa', ['INDUSTRY_SOURCE', 'BRAND_ACTIVATION_OBSERVER',
                    'TECHNICAL_SPEAKER_HUB'], 'HIGH', ['BIOCONTROL'], 'PROVED',
  'NÃO é fonte independente quando os próprios técnicos aparecem. Medido nesta '
  'rodada: patrocina a categoria "Tomatito" dos Premios AgroInfluye — o que a '
  'torna simultaneamente fonte e OBJETO da observação de ativação de marca.',
  'https://seipasa.com/en/news/seipasa-at-the-agroinfluye-2026-awards/'),

 # ───────────────────────────────────────────────────────────────── ITÁLIA
 ('IT', 'EIMA Social Awards', ['AWARD', 'CREATOR_DISCOVERY_HUB'], 'VERY_HIGH',
  ['MACHINERY', 'MULTI_CROP'], 'NOT_TESTED',
  ASSERT + ' · usar edições anteriores + 2026', cr.NAO_SEI),
 ('IT', 'Agrilevante / AGIA-CIA / FederUnacoma',
  ['FIELD_EVENT', 'CREATOR_DISCOVERY_HUB'], 'HIGH', ['MULTI_CROP'], 'NOT_TESTED',
  ASSERT + ' · painéis CONTENT CREATOR / AGRINFLUENCER / FUORI DAI SOCIAL',
  cr.NAO_SEI),
 ('IT', 'Fieragricola Verona', ['FIELD_EVENT', 'FARMER_NETWORK_HUB'], 'HIGH',
  ['MULTI_CROP'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'Enovitis in Campo', ['FIELD_EVENT', 'BRAND_ACTIVATION_OBSERVER'],
  'VERY_HIGH', ['GRAPEVINE', 'CROP_PROTECTION', 'MACHINERY'], 'NOT_TESTED',
  ASSERT + ' · ocorre DENTRO do vinhedo, com viticultores, técnicos, demos de '
  'produto e sessões de crop protection — é o hub italiano mais próximo da '
  'pergunta desta missão', cr.NAO_SEI),
 ('IT', 'CREA Ricerca (e centros por cultura)', ['SCIENCE_HUB'], 'VERY_HIGH',
  ['MULTI_CROP'], 'NOT_TESTED', ASSERT + ' · NÃO é influencer', cr.NAO_SEI),
 ('IT', 'CREA-VE', ['SCIENCE_HUB'], 'VERY_HIGH', ['GRAPEVINE'], 'NOT_TESTED',
  ASSERT, cr.NAO_SEI),
 ('IT', 'CREA-CI', ['SCIENCE_HUB'], 'VERY_HIGH',
  ['DURUM_WHEAT', 'SOFT_WHEAT', 'MAIZE', 'RICE', 'BARLEY'], 'NOT_TESTED',
  ASSERT, cr.NAO_SEI),
 ('IT', 'Fondazione Edmund Mach', ['TECHNICAL_SPEAKER_HUB', 'FIELD_EVENT'],
  'VERY_HIGH', ['GRAPEVINE', 'APPLE', 'PLANT_HEALTH'], 'NOT_TESTED', ASSERT,
  cr.NAO_SEI),
 ('IT', 'CNR-IPSP', ['PLANT_PROTECTION_SCIENCE_HUB'], 'VERY_HIGH',
  ['PLANT_PROTECTION'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'AGROINNOVA · UniTo', ['PLANT_PROTECTION_SCIENCE_HUB'], 'VERY_HIGH',
  ['PLANT_HEALTH', 'CROP_PROTECTION'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'DiSAA · UniMi', ['TECHNICAL_SPEAKER_HUB'], 'HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'DISTAL · UniBo', ['TECHNICAL_SPEAKER_HUB'], 'HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'DAFNAE · UniPd', ['TECHNICAL_SPEAKER_HUB'], 'HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'DISAFA · UniTo', ['TECHNICAL_SPEAKER_HUB'], 'HIGH', ['MULTI_CROP'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'Scuola Superiore Sant\'Anna', ['AGTECH_SOURCE', 'TECHNICAL_SPEAKER_HUB'],
  'MEDIUM', ['AGTECH', 'ROBOTICS', 'CLIMATE'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'Horta srl', ['INDUSTRY_SOURCE', 'TECHNICAL_SPEAKER_HUB'], 'HIGH',
  ['DSS', 'FIELD_TECHNOLOGY'], 'NOT_TESTED',
  ASSERT + ' · separar conteúdo comercial de observação independente',
  cr.NAO_SEI),
 ('IT', 'CIHEAM Bari', ['TECHNICAL_SPEAKER_HUB'], 'HIGH',
  ['OLIVE', 'WATER', 'MEDITERRANEAN_CROPS'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('IT', 'IIT / "IIT Agro"', ['AGTECH_SOURCE'], 'MEDIUM', ['AGTECH'],
  'IDENTITY_NOT_PROVED',
  'O dono da missão instruiu explicitamente: NÃO aceitar "IIT Agro" como '
  'unidade formal sem validação. Papel provisório.', cr.NAO_SEI),
 ('IT', '"Osservatorio Agro"', ['OTHER'], 'LOW', ['NOT_KNOWN'],
  'IDENTITY_NOT_PROVED',
  'Identidade não provada. Instrução do dono: NÃO coletar em volume até '
  'resolver qual entidade é.', cr.NAO_SEI),

 # ───────────────────────────────────────────────────────────────── FRANÇA
 ('FR', "Salon International de l'Agriculture (SIA)",
  ['FIELD_EVENT', 'CREATOR_DISCOVERY_HUB', 'BRAND_ACTIVATION_OBSERVER'],
  'VERY_HIGH', ['MULTI_CROP'], 'PROVED',
  'PRIORIDADE Nº 1 francesa. Já é, nesta rodada, o palco do único caso de '
  'empresa de crop protection patrocinando creator na França (Bayer, 2023). '
  'Tem espaço de creators e interprofissões.',
  'https://www.tiktok.com/@vakitamedia/video/7207500313941544197'),
 ('FR', "Les Blacks Moutons / Espoirs de l'influence agricole",
  ['AWARD', 'CREATOR_DISCOVERY_HUB'], 'VERY_HIGH', ['MULTI_CROP'], 'NOT_TESTED',
  ASSERT + ' · usar vencedores e candidatos como master discovery source',
  cr.NAO_SEI),
 ('FR', 'SITEVI', ['FARMER_NETWORK_HUB', 'TECHNICAL_SPEAKER_HUB',
                   'BRAND_ACTIVATION_OBSERVER'], 'VERY_HIGH',
  ['GRAPEVINE', 'OLIVE', 'ORCHARDS', 'CROP_PROTECTION', 'SPRAYING'],
  'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('FR', 'SIVAL', ['FARMER_NETWORK_HUB', 'TECHNICAL_SPEAKER_HUB',
                  'BRAND_ACTIVATION_OBSERVER'], 'VERY_HIGH',
  ['VEGETABLES', 'ARBORICULTURE', 'GRAPEVINE', 'HORTICULTURE', 'SEEDS',
   'BIOCONTROL', 'CROP_PROTECTION'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('FR', 'Innov-Agri', ['FIELD_EVENT', 'FARMER_NETWORK_HUB',
                       'BRAND_ACTIVATION_OBSERVER'], 'VERY_HIGH',
  ['LARGE_CROPS', 'MACHINERY', 'SPRAYING'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('FR', 'Vegepolys Valley', ['TECHNICAL_SPEAKER_HUB'], 'HIGH',
  ['SPECIALTY_CROPS', 'ARABLE_CROPS'], 'NOT_TESTED', ASSERT, cr.NAO_SEI),
 ('FR', 'Agri Sud-Ouest Innovation', ['TECHNICAL_SPEAKER_HUB'], 'HIGH',
  ['GRAPEVINE', 'BIOSOLUTIONS', 'IPM'], 'NOT_TESTED',
  ASSERT + ' · Nouvelle-Aquitaine e Occitanie', cr.NAO_SEI),
 ('FR', 'La Ferme Digitale', ['AGTECH_SOURCE'], 'MEDIUM', ['AGTECH'],
  'NOT_TESTED', ASSERT + ' · rede de startups/farmers; não é hub de influencer',
  cr.NAO_SEI),
 ('FR', 'Sencrop (Groupe ISAGRI)', ['AGTECH_SOURCE', 'FARMER_NETWORK_HUB'],
  'MEDIUM', ['AGROMET'], 'CORRECTED',
  'Correção do dono: pertence ao Groupe ISAGRI. NÃO tratar como startup '
  'independente sem contextualizar a aquisição.', cr.NAO_SEI),
 ('FR', "Sommet de l'Élevage", ['FIELD_EVENT', 'FARMER_NETWORK_HUB'], 'MEDIUM',
  ['LIVESTOCK', 'FORAGE', 'MAIZE_SILAGE'], 'NOT_TESTED',
  'DEMOTED para crop protection vegetal. Excelente se e quando houver mapa de '
  'pecuária.', cr.NAO_SEI),
 ('FR', 'SIMA / AgriSIMA', ['FIELD_EVENT'], 'LOW', ['MACHINERY'], 'DEMOTED',
  'Correção do dono: o antigo SIMA foi CANCELADO e o AgriSIMA 2026 precisa ser '
  'tratado pelo estado real medido. NÃO usar como master discovery source sem '
  'provar que uma edição ocorreu.', cr.NAO_SEI),
 ('FR', 'AgFunder', ['GLOBAL_MARKET_INTELLIGENCE'], 'LOW', ['AGTECH'],
  'CORRECTED',
  'Correção do dono: RETIRADO do mapa local francês. É inteligência global de '
  'mercado/investimento, não hub francês de descoberta de creators.', cr.NAO_SEI),
]


def montar():
    os.makedirs(cr.BASE, exist_ok=True)
    fora = []
    for i, (pais, nome, papeis, prio, foco, ident, nota, url) in enumerate(HUBS, 1):
        maus = [p for p in papeis if p not in cr.TIPOS_HUB]
        assert not maus, 'papel de hub fora da lista: %s' % maus
        assert prio in cr.PRIORIDADES, 'prioridade invalida: %s' % prio
        fora.append({
            'HUB_ID': 'HUB-%s-%03d' % (pais, i),
            'COUNTRY': pais, 'NAME': nome,
            'ROLES': papeis, 'PRIORITY': prio, 'FOCUS': foco,
            'IDENTITY_STATE': ident,
            'ROLE_SOURCE': ('MEASURED_THIS_ROUND' if ident == 'PROVED'
                            else 'ASSERTED_BY_MISSION_OWNER'),
            'NOTE': nota, 'SOURCE_URL': url,
            'IS_CREATOR': 'NO',
            'LAW': 'hub não entra em ranking de creator — ele é de onde saem nomes',
            'PEOPLE_EXTRACTED': 0,
            'EXTRACTION_STATE': 'NOT_TESTED',
            'CAPTURE_DATE': CAPTURA,
        })

    from collections import Counter
    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'LAW': 'DISCOVERY_HUB != CREATOR. Universidade, feira, associação, prêmio e '
               'empresa não entram no ranking de creators.',
        'COUNT': len(fora),
        'BY_COUNTRY': dict(Counter(h['COUNTRY'] for h in fora)),
        'IDENTITY_STATE': dict(Counter(h['IDENTITY_STATE'] for h in fora)),
        'HUBS': fora,
    }
    with open(os.path.join(cr.BASE, 'DISCOVERY-HUBS.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/DISCOVERY-HUBS.json')
    print('HUBS=%d  %s' % (len(fora), corpo['BY_COUNTRY']))
    print('IDENTIDADE: %s' % corpo['IDENTITY_STATE'])
    for h in fora:
        if h['IDENTITY_STATE'] in ('IDENTITY_NOT_PROVED', 'DEMOTED', 'CORRECTED'):
            print('  %-12s %-34s %s' % (h['IDENTITY_STATE'], h['NAME'][:34],
                                        h['NOTE'][:52]))


if __name__ == '__main__':
    montar()
