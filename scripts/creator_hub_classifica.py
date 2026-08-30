#!/usr/bin/env python3
"""
CLASSIFICAÇÃO DOS DESCOBERTOS POR HUB — só o que o próprio perfil declara.

    python3 scripts/creator_hub_classifica.py

A REGRA DESTE ARQUIVO
-----------------------
Nada aqui é inferido de "parece agro". Cada campo sai de uma frase que a própria
pessoa escreveu na sua bio pública, e `DECLARATION_TYPE` diz isso em todo
registro. É evidência de primeira mão sobre a própria atividade — forte, e de
natureza declarada, que é diferente de conteúdo analisado.

TRÊS COISAS QUE A BIO REVELOU E QUE NENHUMA CONTAGEM REVELARIA
----------------------------------------------------------------
1. **MENÇÃO EM HUB ≠ PAÍS.** `@la_huerta_malagon` escreve "Guanajuato" — é
   MÉXICO. `@ironfarmer_rc` escreve "ÉVORA/PORTUGAL". O AgroInfluye criou
   categoria LATAM nesta edição, então a conta do prêmio menciona gente de fora
   da Espanha. Herdar o país do hub teria posto dois estrangeiros no mapa
   espanhol.

2. **A GRANDE VENCEDORA É DE PECUÁRIA.** `@luciiaacasal` — que levou Maquineros
   E Melhor Creator Agro — escreve "Ganaderia Casal Vazquez SC". Excelente
   creator; **fora** do mapa de proteção de cultivo vegetal.

3. **2,6 MILHÕES DE SEGUIDORES, AUDIÊNCIA ERRADA.** `@lajoya.agro` tem 2.659.403
   seguidores, usa #agroinfluencer — e declara, na própria bio, que explica
   situações de campo *"para gente de Ciudad"*. Ordenar por seguidores o poria em
   primeiro lugar numa ativação dirigida a quem aplica defensivo.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'

# handle: o que a BIO declara. Campo ausente = a bio não disse.

# §0 · COM QUEM o Marketing estaria falando. Tabela explícita porque cada linha
# é um julgamento que precisa poder ser contestado — e não um padrão silencioso.
ENTIDADE_DE_ATIVACAO = {
    # a conta leva o nome da exploração, mas há um creator identificável à frente:
    # a docussérie do Dmax é sobre ele, com o nome dele.
    '@gomierofarm': 'PERSON_CREATOR',
    '@narduccio_capicchiaro': 'PERSON_CREATOR',
    '@Tomy_Rohde': 'PERSON_CREATOR',
    # §0 · A CORREÇÃO: conta corporativa. Não há evidência de que Francisco Jesús
    # Montoya a conduza como creator pessoal — ele é fundador e gerente. Fechar
    # aqui é acordo com uma empresa, não contrato com um creator.
    '@biocampojoyma': 'FARM_BUSINESS',
    '@terruzapistachos': 'FARM_BUSINESS',
    '@nitofrutasyverduras': 'OTHER',          # comércio de fruta e verdura
    '@twinsfarm': 'MEDIA_ACCOUNT',            # "Tu Web de Agricultura"
    '@cumbrerizosfera': 'ORGANIZATION',       # Cumbre Rizosfera
    '@laderasdelnaranco': 'OTHER',            # jardinagem/paisagismo
}
DEFAULT_ENTIDADE = 'PERSON_CREATOR'

DECLARADO = {
 '@huerto_ecologico.marc': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=['OLIVE', 'CAROB', 'VEGETABLES'], regiao=cr.NAO_SEI,
    bio='"Joven agricultor/19 años · Cultivos: olivo, algarrobo, verdura · 3r generación de agricultores"'),
 '@germanagrolife': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=[], regiao='Almería',
    contato='director do @agrolifepodcast — rota profissional pública',
    bio='"Agricultor · Almería · Consejos para tu cultivo · Director @agrolifepodcast"'),
 '@agrosamanta_': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=[], regiao='Níjar, Almería',
    contato='agrosamanta18@gmail.com', contato_tipo='BUSINESS_EMAIL_PUBLISHED_BY_OWNER',
    bio='"Agricultora con las manos llenas de tierra · Almería · Níjar"'),
 '@chicurri_agro': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=['OLIVE', 'GRAPEVINE'], regiao=cr.NAO_SEI,
    viticultura='PROVED', olivicultura='PROVED',
    bio='"Olivar y viñedo sin filtros · Cómo ganar más con tu finca · Experiencia real, no teoría"'),
 '@agriproduccion': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=[], regiao='Córdoba', ja_na_base='ES-CR-002 (Alberto Rojas)',
    bio='"Córdoba · Agricultura 4.0"'),
 '@oliverio_rodfer': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=['GRAPEVINE'], regiao=cr.NAO_SEI, viticultura='PROVED',
    bio='nome do perfil declara "Oliverio Rodriguez Viticultor"'),
 '@terruzapistachos': dict(
    pais='ES', tipo='TECHNICAL_CREATOR', produtor='NOT_KNOWN', facing='FARMER_FACING',
    crops=['PISTACHIO'], regiao='Benamaurel, Granada', entidade='ORGANIZATION',
    bio='"Expertos en todo lo referente al cultivo del pistacho · Benamaurel (Granada)"'),
 '@la_fuina_de_los_monegros': dict(
    pais='ES', tipo='RURAL_LIFESTYLE_CREATOR', produtor='NOT_KNOWN', facing='MIXED',
    crops=[], regiao='Robres, Monegros (Aragón)',
    bio='"Edu Luna (Robres)" — nenhuma cultura declarada'),
 '@agrofamily_moralesperez': dict(
    pais='ES', tipo='RURAL_LIFESTYLE_CREATOR', produtor='NOT_PROVED', facing='MIXED',
    crops=[], regiao=cr.NAO_SEI,
    bio='"Graduada en ADE · Apasionada a la Agricultura · Nieta e hija de agricultores" '
        '— NETA E FILHA de agricultores não é declaração de ser agricultora'),
 '@twinsfarm': dict(
    pais='ES', tipo='AG_MEDIA_CREATOR', produtor='NOT_KNOWN', facing='MIXED',
    crops=[], regiao=cr.NAO_SEI, entidade='ORGANIZATION',
    bio="'Twins Farm. Tu Web de Agricultura. Spain' — é um site, não uma pessoa"),
 '@cumbrerizosfera': dict(
    pais='ES', tipo='INSTITUTIONAL_CREATOR', produtor='NOT_PROVED', facing='TECHNICAL_FACING',
    crops=[], regiao=cr.NAO_SEI, entidade='ORGANIZATION',
    bio='"Cumbre Rizosfera · Innovación para transformar territorios"'),

 # ── pecuária: excelentes creators, FORA do mapa de proteção vegetal
 '@luciiaacasal': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=[], regiao=cr.NAO_SEI, pecuaria=True,
    bio='"Ganaderia Casal Vazquez SC · Nacional Juventud 23" — venceu Maquineros E '
        'Melhor Creator Agro do AgroInfluye 2026'),
 '@valdelmazo': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='PROVED', facing='FARMER_FACING',
    crops=[], regiao=cr.NAO_SEI, pecuaria=True,
    bio='"Marta García Martínez · Actividad: Ganadera ATP · Ganadería Val del Mazo"'),
 '@agri_josette': dict(
    pais='ES', tipo='FARMER_CREATOR', produtor='NOT_KNOWN', facing='FARMER_FACING',
    crops=[], regiao=cr.NAO_SEI, pecuaria=True,
    embaixador=['@tatomaagro', '@maschiogaspardo'],
    bio='"Campo, ganado y maquinaria · Embajador de @tatomaagro y @maschiogaspardo"'),

 # ── consumer-facing: podem servir a B2C, não à ativação junto a quem aplica
 '@lajoya.agro': dict(
    pais='ES', tipo='AG_MEDIA_CREATOR', produtor='NOT_KNOWN', facing='GENERAL_CONSUMER',
    crops=[], regiao=cr.NAO_SEI,
    bio='"Ingeniero · Explico situaciones de Campo PARA GENTE DE CIUDAD · #agroinfluencer" '
        '— 2.659.403 seguidores e a audiência declarada pela própria bio é urbana'),
 '@urrapetito': dict(
    pais='ES', tipo='FOOD_CREATOR', produtor='NOT_KNOWN', facing='FOOD_CONSUMER',
    crops=[], regiao=cr.NAO_SEI,
    contato='urra@thehungeragency.com', contato_tipo='AGENCY',
    bio='"La comida de verdad" · e-mail de agência'),
 '@nitofrutasyverduras': dict(
    pais='ES', tipo='FOOD_CREATOR', produtor='NOT_PROVED', facing='FOOD_CONSUMER',
    crops=[], regiao='Canárias', entidade='ORGANIZATION',
    bio='"Enviamos fruta y verdura a toda Canarias · Pedidos web" — é COMÉRCIO de '
        'fruta e verdura. Venceu a categoria Tomatito, patrocinada pela Seipasa.'),
 '@lahortetadebussy': dict(
    pais='ES', tipo='FOOD_CREATOR', produtor='NOT_KNOWN', facing='GENERAL_CONSUMER',
    crops=[], regiao=cr.NAO_SEI,
    bio='"Te ayudo en el Huerto y con tus Plantas · Venta verduras en el huerto Sábados"'),
 '@angel_illescas_': dict(
    pais='ES', tipo='OTHER', produtor='NOT_KNOWN', facing='GENERAL_CONSUMER',
    crops=[], regiao=cr.NAO_SEI,
    contato='angelillescasnombela@hotmail.com', contato_tipo='BUSINESS_EMAIL_PUBLISHED_BY_OWNER',
    bio='"Te ayudo a cuidar tus plantas" — plantas domésticas'),
 '@laderasdelnaranco': dict(
    pais='ES', tipo='OTHER', produtor='NOT_PROVED', facing='GENERAL_CONSUMER',
    crops=[], regiao=cr.NAO_SEI,
    contato='hola@laderasdelnaranco.com', contato_tipo='BUSINESS_EMAIL_PUBLISHED_BY_OWNER',
    bio='"TS en Jardinería y Restauración del Paisaje" — jardinagem ornamental'),

 # ── MENÇÃO EM HUB != PAÍS
 '@la_huerta_malagon': dict(
    pais='MX', tipo='AGRONOMIST_CREATOR', produtor='NOT_KNOWN', facing='FARMER_FACING',
    crops=[], regiao='Guanajuato', fora_do_mapa_es=True,
    bio='"Tu Agrónomo Favorito · Guanajuato" — MÉXICO, não Espanha'),
 '@ironfarmer_rc': dict(
    pais='PT', tipo='TECHNICAL_CREATOR', produtor='NOT_KNOWN', facing='FARMER_FACING',
    crops=[], regiao='Évora', fora_do_mapa_es=True,
    bio='"LÍDER DE OPINIÃO · AGRICULTURA · PALESTRAS · ÉVORA/PORTUGAL" — PORTUGAL'),
}


def montar():
    perfis = {p['HANDLE'].lower(): p for p in cr.carregar('HUB-DISCOVERED-RESOLVED.json')}
    fora, pecuaria, estrangeiros = [], [], []

    for handle, d in DECLARADO.items():
        p = perfis.get(handle.lower(), {})
        r = cr.registro_vazio()
        crops = d.get('crops') or []
        r.update({
            'CREATOR_ID': 'ES-HUB-%s' % handle.lstrip('@').lower()[:22],
            'ORIGIN_ID': handle, 'NAME': p.get('FULL_NAME', cr.NAO_SEI),
            'DISPLAY_NAME': handle,
            'COUNTRY': d['pais'], 'LANGUAGE': 'es' if d['pais'] == 'ES' else cr.NAO_SEI,
            'REGION': d.get('regiao', cr.NAO_SEI),
            'REGIONS': [d['regiao']] if d.get('regiao', cr.NAO_SEI) != cr.NAO_SEI else cr.NAO_SEI,
            'ENTITY_KIND': d.get('entidade', 'PERSON'),
            'OCCUPATION': d['bio'],
            'CREATOR_TYPE': d['tipo'], 'FACING': d['facing'],
            'ACTUAL_FARMER': d['produtor'],
            'ACTUAL_FARMER_EVIDENCE': 'declarado na própria bio pública: %s' % d['bio'],
            'FARMER_CREATOR_ROLE': 'YES' if d['produtor'] == 'PROVED' else 'NOT_KNOWN',
            'ACTIVATION_CREATOR': 'NOT_KNOWN', 'TECHNICAL_SENSOR_CANDIDATE': 'NOT_KNOWN',
            'FIELD_VOICE_SOURCE': 'NOT_KNOWN', 'SENSOR_ROLE_LINK': 'NOT_LINKED',
            'CROPS': crops or cr.NAO_SEI,
            'CROP_STATE': 'PROVED' if crops else 'NOT_PROVED',
            'CROP_EVIDENCE': ('cultura declarada pela própria pessoa na bio pública: %s'
                              % d['bio']) if crops else 'a bio não declara cultura',
            'CROP_PROVED_BY_CONTENT': crops or cr.NAO_SEI,
            'CROP_PROOF_URLS': [p.get('PROFILE_URL', cr.NAO_SEI)],
            'DECLARATION_TYPE': 'SELF_DECLARED_PUBLIC_PROFILE',
            'INSTAGRAM': handle, 'PLATFORMS': ['INSTAGRAM'],
            'PROFILE_URL': p.get('PROFILE_URL', cr.NAO_SEI),
            'HANDLE_EXISTS': p.get('HANDLE_EXISTS', 'NOT_TESTED'),
            'ACTIVATION_ENTITY_TYPE': ENTIDADE_DE_ATIVACAO.get(handle, DEFAULT_ENTIDADE),
            'NAME_MATCH': 'NOT_TESTED',
            'FOLLOWERS_BY_PLATFORM': ({'INSTAGRAM': p['FOLLOWERS']}
                                      if isinstance(p.get('FOLLOWERS'), int) else cr.NAO_SEI),
            'AS_OF_DATE': p.get('AS_OF_DATE', CAPTURA),
            'ACTIVITY_STATE': p.get('ACTIVITY_STATE', 'NOT_MEASURED'),
            'LAST_ACTIVITY_DATE': p.get('LAST_ACTIVITY_DATE', cr.NAO_SEI),
            'POSTS_LAST_30D': p.get('POSTS_LAST_30D', cr.NAO_SEI),
            'POSTS_LAST_90D': p.get('POSTS_LAST_90D', cr.NAO_SEI),
            'IDENTITY_STATE': 'PROVED' if p.get('HANDLE_EXISTS') == 'YES' else 'NOT_PROVED',
            'IDENTITY_EVIDENCE': 'perfil público resolvido pela rota Apify e bio própria lida',
            'AUDIENCE_TYPE': 'NOT_KNOWN',
            'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN', 'BRAND_RELATION_TYPE': 'NOT_KNOWN',
            'ADAMA_COLLABORATION_OBSERVED': 'NOT_OBSERVED',
            'PUBLIC_CONTACT_ROUTE': d.get('contato', cr.NAO_SEI),
            'CONTACT_KIND': d.get('contato_tipo', cr.NAO_SEI),
            'SOURCE_URL': p.get('PROFILE_URL', cr.NAO_SEI),
            'SOURCE_KIND': 'HUB_MENTION + PROFILE_BIO',
            'SOURCE_ID': MISSION, 'CAPTURE_DATE': CAPTURA,
            'COLLECTION_ROUTE': 'apify: extração de menções do @agroinfluye + resolução de perfil',
            'DISCOVERY_ROUTES': p.get('DISCOVERED_VIA') or ['Premios AgroInfluye'],
        })
        for c in ('WINE_RELEVANCE', 'VITICULTURE_RELEVANCE',
                  'OLIVE_OIL_RELEVANCE', 'OLIVE_GROWING_RELEVANCE'):
            r[c] = 'NOT_KNOWN'
        # Quem declara a cultura como LAVOURA PRÓPRIA prova a cadeia agrícola —
        # é o contrário do sommelier, que declara o produto pronto. A distinção
        # não está no nome da cultura, está em QUEM diz e em que posição.
        if d['produtor'] == 'PROVED':
            if 'OLIVE' in crops:
                r['OLIVE_GROWING_RELEVANCE'] = 'PROVED'
            if 'GRAPEVINE' in crops:
                r['VITICULTURE_RELEVANCE'] = 'PROVED'
        if d.get('viticultura'):
            r['VITICULTURE_RELEVANCE'] = d['viticultura']
        if d.get('olivicultura'):
            r['OLIVE_GROWING_RELEVANCE'] = d['olivicultura']
        if d.get('embaixador'):
            r['BRAND_RELATIONSHIP_STATE'] = 'BRAND_COLLABORATION_PROVED'
            r['BRAND_RELATION_TYPE'] = 'BRAND_COLLABORATION_PROVED'
            r['BRAND_COLLABORATIONS'] = d['embaixador']

        fit, porque = cr.fit_para_adama(r)
        r['AUDIENCE_FIT_FOR_ADAMA'] = fit
        estado, porques = cr.relevancia(r)
        r['RELEVANCE_STATE'] = estado
        extras = ['FIT_ADAMA=%s: %s' % (fit, porque), 'BIO_DECLARADA: %s' % d['bio']]
        if d.get('pecuaria'):
            r['LIVESTOCK_CREATOR'] = 'YES'
            extras.append('PECUARIA: fora do mapa de proteção de cultivo VEGETAL — '
                          'ótimo candidato se e quando houver mapa de pecuária')
            pecuaria.append(handle)
        else:
            r['LIVESTOCK_CREATOR'] = 'NO'
        if d.get('fora_do_mapa_es'):
            extras.append('PAIS_DIFERENTE_DO_HUB: mencionado pela conta do prêmio '
                          'espanhol, mas a bio declara %s' % d['pais'])
            estrangeiros.append(handle)
        if d.get('ja_na_base'):
            extras.append('JA_NA_BASE: %s — mesma pessoa, rota de descoberta nova'
                          % d['ja_na_base'])
        r['WHY_RELEVANT'] = porques + extras

        faltas = cr.checar(r)
        if faltas:
            print('PORTAO %s: %s' % (handle, faltas)); raise SystemExit(1)
        fora.append(r)

    from collections import Counter
    es_vegetal = [r for r in fora if r['COUNTRY'] == 'ES'
                  and r.get('LIVESTOCK_CREATOR') == 'NO']
    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'LAW': 'Nada aqui é inferido de "parece agro". Cada campo sai de uma frase que a '
               'própria pessoa escreveu na bio pública — DECLARATION_TYPE diz isso.',
        'COUNT': len(fora),
        'BY_COUNTRY': dict(Counter(r['COUNTRY'] for r in fora)),
        'BY_FACING': dict(Counter(r['FACING'] for r in fora)),
        'BY_STATE': dict(Counter(r['RELEVANCE_STATE'] for r in fora)),
        'BY_FIT': dict(Counter(r['AUDIENCE_FIT_FOR_ADAMA'] for r in fora)),
        'LIVESTOCK_EXCLUDED_FROM_CROP_MAP': pecuaria,
        'HUB_MENTION_IS_NOT_COUNTRY': estrangeiros,
        'ES_VEGETAL_POOL': len(es_vegetal),
        'CREATORS': fora,
    }
    with open(os.path.join(cr.BASE, 'HUB-DISCOVERED-CLASSIFIED.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: HUB-DISCOVERED-CLASSIFIED.json')
    print('POR_PAIS:', corpo['BY_COUNTRY'])
    print('POR_FACING:', corpo['BY_FACING'])
    print('POR_ESTADO:', corpo['BY_STATE'])
    print('FIT_ADAMA:', corpo['BY_FIT'])
    print('PECUARIA (fora do mapa vegetal):', pecuaria)
    print('MENCIONADOS PELO HUB ES MAS DE OUTRO PAIS:', estrangeiros)


if __name__ == '__main__':
    montar()
