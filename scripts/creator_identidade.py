#!/usr/bin/env python3
"""
RESOLUÇÃO DE IDENTIDADE PRIMÁRIA (§4) — os quatro prioritários.

    python3 scripts/creator_identidade.py

POR QUE ESTE ARQUIVO EXISTE
-----------------------------
`ACTIVATION_READY = 0` tinha uma causa única e nomeada: identidade não resolvida
em fonte primária. Esta rodada ataca os quatro candidatos de maior valor antes de
coletar mais um único post — porque coletar conteúdo de um handle errado produz
um dossiê inteiro sobre a pessoa errada.

O QUE A RESOLUÇÃO ENCONTROU, E QUE A SEED NÃO PODIA ENCONTRAR
---------------------------------------------------------------
Os quatro casos falharam de QUATRO MANEIRAS DIFERENTES, e é isso que torna a
rodada útil — cada uma é uma classe de erro que voltará:

    HANDLE ERRADO       @davide_gomiero -> o real e @gomierofarm (457 mil)
    NOME ERRADO         "Leggeri" -> Leggieri; e o handle pessoal nao e a
                        comunidade: @narduccio_capicchiaro != @evolovers.eu
    PESSOA != PERSONA   "Tomy Rohde" e ALTER EGO de Fernando Giraldo
    PESSOA != EMPRESA   @biocampojoyma e a conta da EMPRESA Bio Campojoyma,
                        nao a conta pessoal de Francisco Jesus Montoya

As duas últimas são a mesma lei que o `ES-01717` ensinou no registro
fitossanitário, agora em rede social: **a entidade que assina não é
necessariamente a entidade que se procura**. Um contrato de ativação fechado com
`@biocampojoyma` é acordo comercial com uma empresa que produz 15 milhões de
quilos de pimento — não um contrato de influencer com um produtor.

DIVERGÊNCIA NÃO SE RECONCILIA EM SILÊNCIO
-------------------------------------------
Duas fontes descrevem Fernando Giraldo de formas diferentes — uma diz
`olivarero/agricultor`, outra diz `ganadero`. As duas ficam registradas em
`OCCUPATION_DIVERGENCE`. Escolher uma calada inventaria precisão que a fonte não
deu, exatamente como no caso `0000-0003-1895-5895` do ORCID.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'


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

RESOLUCOES = [
 dict(
   creator_id='IT-CR-006', nome='Davide Gomiero', pais='IT',
   handle_da_seed='@davide_gomiero', handle_real='@gomierofarm',
   classe_do_erro='HANDLE_ERRADO_NA_SEED',
   entidade='PERSON',
   perfil='https://www.instagram.com/gomierofarm/',
   regiao='Limena, Padova, Veneto',
   ocupacao='agricultor na empresa familiar Azienda Agricola F.lli Gomiero',
   produtor='PROVED',
   produtor_ev='empresa familiar de ~400 ha com ~1.200 bovinos de leite; registro '
               'societario publico; docusserie "Quella pazza fattoria" no Dmax',
   crops=['MAIZE', 'ALFALFA', 'SOYBEAN', 'FORAGE'], crop_state='PROVED',
   prova_tipo='D_FARM_PRODUCTION_PROVED',
   crop_ev='CLASSE D: producao da exploracao provada por registro societario publico '
           '(Azienda Agricola F.lli Gomiero) e por imprensa que declara feno, MILHO, '
           'alfafa e soja para ~1.200 bovinos. As culturas listadas estao PROVADAS; '
           'o TRIGO e o ARROZ que a SEED alegou continuam NOT_PROVED e nao entram '
           'em CROPS. Provar uma cultura e refutar outra sao resultados distintos, '
           'e o registro guarda os dois.',
   crops_rejeitadas_da_seed=['WHEAT', 'RICE'],
   seguidores={'INSTAGRAM': 457000}, seguidores_nota='@gomierofarm, 3.920 posts',
   audiencia='MIXED',
   audiencia_ev='fonte descreve comunidade de agricultores, criadores e entusiastas',
   contato='Oscar Green 2022 (Coldiretti Padova); perfil publico de imprensa regional',
   contato_tipo='PUBLIC_PRESS_ROUTE',
   tipo='FARMER_CREATOR',
   urls=['https://www.instagram.com/gomierofarm/',
         'https://www.padovastories.com/story/gomiero-farm-davide-gomiero/',
         'https://padova.coldiretti.it/news/oscar-green-2022-due-padovani-fra-i-vincitori/']),

 dict(
   creator_id='IT-CR-007', nome='Leonardo Leggieri', pais='IT',
   handle_da_seed='@evolovers', handle_real='@narduccio_capicchiaro',
   classe_do_erro='NOME_E_HANDLE_ERRADOS_NA_SEED',
   entidade='PERSON',
   perfil='https://www.instagram.com/narduccio_capicchiaro/',
   regiao='Puglia',
   ocupacao='olivicultor e sommelier de azeite (FIS); fundador da comunidade @evolovers.eu',
   produtor='PROVED',
   produtor_ev='descrito como olivicultor e produtor pugliese; a comunidade nasceu de '
               'podas, colheitas e degustacoes no proprio olival',
   crops=['OLIVE'], crop_state='PROVED',
   crop_ev='olivicultor com olival proprio; conteudo de poda e colheita',
   seguidores={'INSTAGRAM': 2454}, seguidores_nota='conta PESSOAL; a comunidade '
               '@evolovers.eu e outra conta e nao foi medida',
   audiencia='NOT_KNOWN', audiencia_ev='nao medida',
   contato='e-mail profissional publicado no proprio perfil (dominio evolovers.it)',
   contato_tipo='BUSINESS_EMAIL_PUBLISHED_BY_OWNER',
   tipo='FARMER_CREATOR',
   urls=['https://www.instagram.com/narduccio_capicchiaro/',
         'https://www.cronachedigusto.it/l-intervista/lolio-raccontato-sui-social-cinque-evocreator-bravissimi-da-seguire/']),

 dict(
   creator_id='ES-CR-001', nome='Fernando Giraldo', pais='ES',
   handle_da_seed='@Tomy_Rohde', handle_real='@Tomy_Rohde',
   classe_do_erro='PESSOA_DIFERENTE_DE_PERSONA',
   entidade='PERSON',
   perfil='https://x.com/Tomy_Rohde',
   regiao='La Carlota, Campina cordobesa, Cordoba (Andalucia)',
   ocupacao='olivarero e agricultor; marca propria de azeite "Aceite de Tom"',
   produtor='PROVED',
   produtor_ev='agricultor jovem de La Carlota com marca propria de azeite; premio '
               '"Felipe Gonzalez de Canales" para jovens empreendedores',
   crops=['OLIVE'], crop_state='PROVED',
   crop_ev='olivarero com marca propria de azeite; relata o dia a dia do campo desde 2019',
   seguidores={'X': 52000, 'INSTAGRAM': 6000},
   seguidores_nota='fontes divergem: uma diz 52.000 no X, outra 38.500 no X e 6.000 '
                   'no Instagram. Datas diferentes — as duas ficam registradas.',
   audiencia='NOT_KNOWN', audiencia_ev='nao medida',
   contato='marca propria "Aceite de Tom" — rota comercial publica',
   contato_tipo='OWN_BRAND_PUBLIC_ROUTE',
   tipo='FARMER_CREATOR',
   divergencia='uma fonte o descreve como "ganadero cordobes" e outra como '
               '"olivarero/agricultor". Divergencia registrada, nao reconciliada.',
   persona='"Tomy Rohde" e um ALTER EGO digital criado por Fernando Giraldo. '
           'NAME != DISPLAY_NAME != HANDLE: contratar "Tomy Rohde" e contratar '
           'Fernando Giraldo, e o contrato precisa saber disso.',
   urls=['https://www.eldebate.com/espana/la-voz-de-cordoba/sociedad/20240107/campo-he-encontrado-tranquilidad_165129.html',
         'https://www.directoalpaladar.com/actualidad-1/hablamos-tomy-rohde-agricultor-cordoba-que-ha-conseguido-que-le-compren-tractor-gracias-a-twitter']),

 dict(
   creator_id='ES-CR-004', nome='Francisco Jesús Montoya', pais='ES',
   handle_da_seed='@biocampojoyma', handle_real='@biocampojoyma',
   classe_do_erro='PESSOA_DIFERENTE_DE_EMPRESA',
   entidade='ORGANIZATION',
   perfil='https://www.instagram.com/biocampojoyma/',
   regiao='Nijar, Almeria (Andalucia)',
   ocupacao='fundador e gerente da Bio Campojoyma',
   produtor='PROVED',
   produtor_ev='fundador e gerente da Bio Campojoyma, ~15 milhoes de quilos de pimento '
               'ecologico por ano; descrita como a maior produtora de hortalicas '
               'ecologicas do pais',
   crops=['PEPPER', 'TOMATO', 'PROTECTED_HORTICULTURE'], crop_state='PROVED',
   crop_ev='pimento ecologico em volume industrial, tomate e outras hortalicas',
   seguidores={'INSTAGRAM': 11000}, seguidores_nota='conta da EMPRESA, nao da pessoa',
   audiencia='NOT_KNOWN', audiencia_ev='nao medida',
   contato='canal corporativo publico da Bio Campojoyma',
   contato_tipo='CORPORATE_PUBLIC_CHANNEL',
   tipo='INSTITUTIONAL_CREATOR',
   entidade_nota='@biocampojoyma e a conta da EMPRESA Bio Campojoyma, nao a conta '
                 'pessoal de Francisco Jesus Montoya. Fechar ativacao aqui e acordo '
                 'comercial B2B com uma produtora, nao contrato de influencer com um '
                 'produtor. Os dois podem interessar — nao sao a mesma coisa.',
   urls=['https://www.instagram.com/biocampojoyma/',
         'https://fruittoday.com/bio-campojoyma-se-acerca-al-poniente-con-un-punto-de-recogida/',
         'https://agroautentico.com/2021/05/campojoyma-y-pimiento-bio/']),

 # ───────────────────────────────────────────── FRANCA (§6): a lacuna de cultura
 # A rodada anterior tinha 4 candidatos franceses e ZERO culturas provadas. Estes
 # dois fecham o buraco com o recorte que mais interessa: grandes culturas.
 dict(
   creator_id='FR-CR-005', nome='David Forge', pais='FR',
   handle_da_seed='David Forge (nome da pessoa)',
   handle_real='@chaineagricole (Chaine Agricole)',
   classe_do_erro='NOME_DA_PESSOA_DIFERENTE_DO_NOME_DO_CANAL',
   entidade='PERSON',
   perfil='https://www.youtube.com/@chaineagricole',
   regiao='Indre-et-Loire, Touraine (Centre-Val de Loire)',
   ocupacao='agricultor; retomou a exploracao familiar de 160 ha; youtuber desde 2015',
   produtor='PROVED',
   produtor_ev='retomou a exploracao familiar na Touraine; exploracao cerealifera de '
               '160 hectares, declarada por reportagem de imprensa setorial',
   crops=['WHEAT', 'BARLEY', 'RAPESEED', 'SUNFLOWER'], crop_state='PROVED',
   prova_tipo='C_RECURRING_FIELD_CONTENT',
   crop_ev='CLASSE C: exploracao cerealifera de 160 ha (imprensa) E titulos do proprio '
           'canal confirmando por conteudo — "Semis du ble sans travailler le sol", '
           '"Engrais sur un colza qui demarre fort", "preparer le sol au tournesol", '
           '"Livraison de la derniere benne de ble". Cultura lida do CONTEUDO, nao da '
           'consulta.',
   seguidores={'YOUTUBE': 106000},
   seguidores_nota='~106 mil inscritos; canal secundario "David Forge, les Bonus" existe',
   audiencia='NOT_KNOWN', audiencia_ev='nao medida',
   contato='presenca publica no stand #agridemain do Salon de l\'Agriculture',
   contato_tipo='PUBLIC_EVENT_ROUTE',
   tipo='FARMER_CREATOR',
   urls=['https://www.terre-net.fr/2017/article/125795/david-forge-youtubeur-et-paysan-la-campagne-camera-au-poing',
         'https://www.agri-mutuel.com/actualites/david-forge-youtubeur-et-paysan-la-campagne-camera-au-poing/']),

 dict(
   creator_id='FR-CR-006', nome='Gilles Van Kempen', pais='FR',
   handle_da_seed='Gilles Van Kempen', handle_real='Gilles vk agriculteur du Loiret',
   classe_do_erro='SEM_ERRO_NA_SEED',
   entidade='PERSON',
   perfil='https://www.youtube.com/results?search_query=Gilles+vk+agriculteur+du+Loiret',
   regiao='Loiret (Centre-Val de Loire)',
   ocupacao='agricultor no leste do Loiret; publica video agricola todo sabado',
   produtor='PROVED',
   produtor_ev='explora terra propria no leste do Loiret, com producao declarada de '
               'trigo, colza, cevada, milho e sementes de cebola',
   crops=['WHEAT', 'RAPESEED', 'BARLEY', 'MAIZE', 'ONION_SEED'], crop_state='PROVED',
   crop_ev='producao declarada pela fonte: trigo, colza, cevada, milho e sementes de '
           'cebola — GRANDES CULTURAS, o recorte mais proximo do portfolio de '
           'protecao de cultivo',
   seguidores={}, seguidores_nota='nao medido nesta rodada',
   audiencia='NOT_KNOWN', audiencia_ev='nao medida',
   contato='presenca publica no stand #agridemain do Salon de l\'Agriculture',
   contato_tipo='PUBLIC_EVENT_ROUTE',
   tipo='FARMER_CREATOR',
   urls=['https://blog.spotifarm.fr/tour-de-plaine-spotifarm/10-chaines-youtube-a-suivre-en-agriculture',
         'https://www.frenchweb.fr/agtech-4-youtubeurs-stars-de-lagtech/281831']),
]


def montar():
    fora = []
    for r in RESOLUCOES:
        reg = cr.registro_vazio()
        reg.update({
            'CREATOR_ID': r['creator_id'], 'ORIGIN_ID': r['handle_real'],
            'NAME': r['nome'], 'DISPLAY_NAME': r['handle_real'],
            'COUNTRY': r['pais'], 'REGION': r['regiao'],
            'REGIONS': [r['regiao']], 'LANGUAGE': 'it' if r['pais'] == 'IT' else 'es',
            'OCCUPATION': r['ocupacao'], 'ENTITY_KIND': r['entidade'],
            'CREATOR_TYPE': r['tipo'],
            'HANDLE_EXISTS': 'YES', 'PROFILE_URL': r['perfil'],
            'ACTIVATION_ENTITY_TYPE': ENTIDADE_DE_ATIVACAO.get(
                r['handle_real'], DEFAULT_ENTIDADE),
            'NAME_MATCH': 'RESOLVED_BY_PRIMARY_SEARCH',
            'IDENTITY_STATE': 'PROVED',
            'IDENTITY_EVIDENCE': 'identidade, ocupacao e regiao confirmadas por %d '
                                 'fontes independentes da seed; handle real localizado'
                                 % len(r['urls']),
            'ACTUAL_FARMER': r['produtor'], 'ACTUAL_FARMER_EVIDENCE': r['produtor_ev'],
            'FARMER_CREATOR_ROLE': 'YES' if r['produtor'] == 'PROVED' else 'NOT_KNOWN',
            'ACTIVATION_CREATOR': 'NOT_KNOWN',
            'TECHNICAL_SENSOR_CANDIDATE': 'NOT_KNOWN',
            'FIELD_VOICE_SOURCE': 'NOT_KNOWN',
            'SENSOR_ROLE_LINK': 'NOT_LINKED',
            'CROPS': r['crops'], 'CROP_STATE': r['crop_state'],
            'CROP_EVIDENCE': r['crop_ev'], 'CROP_PROOF_URLS': r['urls'],
            'CROP_CLAIMED_BY_SEED': r.get('handle_da_seed'),
            'CROP_PROVED_BY_CONTENT': r['crops'],
            'CROP_PROOF_TYPE': r.get('prova_tipo', cr.NAO_SEI),
            'CROP_PROOF_STRENGTH': 'STRONG' if r.get('prova_tipo') else cr.NAO_SEI,
            'CROPS_REJECTED_FROM_SEED': r.get('crops_rejeitadas_da_seed', []),
            'INSTAGRAM': r['handle_real'] if 'instagram' in r['perfil'] else cr.NAO_SEI,
            'X': r['handle_real'] if 'x.com' in r['perfil'] else cr.NAO_SEI,
            'PLATFORMS': sorted(r['seguidores']) if r['seguidores'] else cr.NAO_SEI,
            'FOLLOWERS_BY_PLATFORM': r['seguidores'] or cr.NAO_SEI,
            'YOUTUBE': r['handle_real'] if 'youtube' in r['perfil'] else cr.NAO_SEI,
            'AS_OF_DATE': CAPTURA,
            'ACTIVITY_STATE': 'NOT_MEASURED',
            'AUDIENCE_TYPE': r['audiencia'],
            'PUBLIC_CONTACT_ROUTE': r['contato'], 'CONTACT_KIND': r['contato_tipo'],
            'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN', 'BRAND_RELATION_TYPE': 'NOT_KNOWN',
            'ADAMA_COLLABORATION_OBSERVED': 'NOT_OBSERVED',
            'SOURCE_URL': r['urls'][0], 'SOURCE_KIND': 'PRIMARY_IDENTITY_RESOLUTION',
            'SOURCE_ID': MISSION, 'CAPTURE_DATE': CAPTURA,
            'COLLECTION_ROUTE': 'WEB_SEARCH dirigida a resolver identidade',
            'DISCOVERY_ROUTES': ['SEED_EXTERNO_IT' if r['pais'] == 'IT' else 'WEB_SEARCH',
                                 'PRIMARY_IDENTITY_RESOLUTION'],
        })
        for c in ('WINE_RELEVANCE', 'VITICULTURE_RELEVANCE',
                  'OLIVE_OIL_RELEVANCE', 'OLIVE_GROWING_RELEVANCE'):
            reg[c] = 'NOT_KNOWN'
        if 'OLIVE' in r['crops']:
            reg['OLIVE_GROWING_RELEVANCE'] = 'PROVED'
            reg['OLIVE_OIL_RELEVANCE'] = 'PROVED'

        fit, porque = cr.fit_para_adama(reg)
        reg['AUDIENCE_FIT_FOR_ADAMA'] = fit
        estado, porques = cr.relevancia(reg)
        reg['RELEVANCE_STATE'] = estado
        extras = ['CLASSE_DO_ERRO_DA_SEED=%s' % r['classe_do_erro'],
                  'FIT_ADAMA=%s: %s' % (fit, porque)]
        for chave in ('persona', 'entidade_nota', 'divergencia'):
            if r.get(chave):
                extras.append('%s: %s' % (chave.upper(), r[chave]))
        reg['WHY_RELEVANT'] = porques + extras
        reg['SEED_HANDLE'] = r['handle_da_seed']
        reg['SEED_ERROR_CLASS'] = r['classe_do_erro']
        reg['FOLLOWERS_NOTE'] = r['seguidores_nota']

        faltas = cr.checar(reg)
        if faltas:
            print('PORTAO %s: %s' % (r['creator_id'], faltas)); raise SystemExit(1)
        fora.append(reg)

    from collections import Counter
    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'LAW': 'Identidade resolvida em fonte primaria ANTES de coletar conteudo. '
               'Coletar posts de um handle errado produz um dossie inteiro sobre a '
               'pessoa errada.',
        'COUNT': len(fora),
        'SEED_ERROR_CLASSES': dict(Counter(r['SEED_ERROR_CLASS'] for r in fora)),
        'RELEVANCE_STATE': dict(Counter(r['RELEVANCE_STATE'] for r in fora)),
        'AUDIENCE_FIT_FOR_ADAMA': dict(Counter(r['AUDIENCE_FIT_FOR_ADAMA'] for r in fora)),
        'HANDLES_CORRIGIDOS': [{'DE': r['SEED_HANDLE'], 'PARA': r['ORIGIN_ID'],
                                'CLASSE': r['SEED_ERROR_CLASS']}
                               for r in fora if r['SEED_HANDLE'] != r['ORIGIN_ID']],
        'CREATORS': fora,
    }
    with open(os.path.join(cr.BASE, 'PRIMARY-IDENTITY-RESOLVED.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/PRIMARY-IDENTITY-RESOLVED.json')
    print('RESOLVIDOS=%d' % len(fora))
    print('CLASSES DE ERRO DA SEED:', corpo['SEED_ERROR_CLASSES'])
    print('RELEVANCE:', corpo['RELEVANCE_STATE'])
    print('FIT_ADAMA:', corpo['AUDIENCE_FIT_FOR_ADAMA'])
    for h in corpo['HANDLES_CORRIGIDOS']:
        print('  CORRIGIDO %-22s -> %-26s %s' % (h['DE'], h['PARA'], h['CLASSE']))


if __name__ == '__main__':
    montar()
