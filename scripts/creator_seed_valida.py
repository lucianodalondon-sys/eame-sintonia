#!/usr/bin/env python3
"""
VALIDAÇÃO DA SEED ITALIANA — o que foi MEDIDO, em arquivo separado do que foi
ALEGADO.

    python3 scripts/creator_seed_valida.py montar

POR QUE SEPARADO DE `creator_seed_it.py`
------------------------------------------
`SEED-IT-CANDIDATES.json` guarda a alegação e não muda. Este arquivo guarda a
medição. Sobrescrever a alegação com a medição apagaria a única coisa capaz de
responder à pergunta que o dono fez: *quantos seeds estavam errados?* Uma
tabela que se autocorrige perde a própria taxa de erro.

O QUE ESTA RODADA MEDIU — E O QUE ELA REFUTOU
-----------------------------------------------
A suspeita lexical (`SUSPECTED_CHAIN_MISMATCH`) acertou em três casos e
**errou em um**, e o erro é o mais instrutivo:

    @evolovers   suspeito por "EVO = azeite, produto final"
                 MEDIDO: Leonardo Leggeri é PRODUTOR pugliese. A comunidade
                 nasceu de podas, colheitas e degustações NO CAMPO DELE.
                 A seed estava CERTA e a nossa suspeita, ERRADA.

É exatamente por isso que `SUSPECTED_CHAIN_MISMATCH` nunca promove sozinho a
`WRONG_ASSIGNMENT`. Um portão que confiasse na suspeita teria descartado o
melhor olivicultor da lista por causa do nome do handle.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'
ROTA = 'WEB_SEARCH — resumo do buscador; páginas não abertas (egresso bloqueado)'

# handle: o que a medição encontrou. Campo vazio = não medido nesta rodada.
MEDIDO = {
 '@doctor.wine': dict(
    nome='Daniele Cernilli', tipo='WINE_MEDIA_CREATOR', regiao='Roma',
    ocupacao='crítico enológico e jornalista; diretor do DoctorWine e da Guida '
             'Essenziale ai Vini d\'Italia; cofundador do Gambero Rosso',
    produtor='NOT_PROVED',
    produtor_ev='40+ anos como jornalista e degustador. Nenhuma fonte o liga a '
                'exploração agrícola própria.',
    crop_state='WRONG_ASSIGNMENT',
    crop_ev='a seed o atribuiu a VITICULTURA. É crítica e guia de VINHO — produto '
            'final. Nenhum conteúdo de manejo, doença ou produção de uva.',
    cadeia={'WINE_RELEVANCE': 'PROVED', 'VITICULTURE_RELEVANCE': 'NOT_PROVED'},
    urls=['https://www.doctorwine.it/chi-siamo',
          'https://www.romatoday.it/cibo/storie/daniele-cernilli-storia-lavoro-guida-vino.html']),

 '@thewinekiller': dict(
    nome='Luca Gardini', tipo='WINE_MEDIA_CREATOR', regiao='Emilia-Romagna / Milano',
    ocupacao='sommelier e crítico de vinho; Melhor Sommelier do Mundo 2010; '
             'curador do guia de 1000 vinhos de L\'Espresso; ~2000 provas/ano',
    produtor='NOT_PROVED',
    produtor_ev='carreira inteira em degustação e crítica; nenhuma exploração própria citada',
    crop_state='WRONG_ASSIGNMENT',
    crop_ev='atribuído a VITICULTURA pela seed; a atividade é prova e pontuação de '
            'vinho pronto',
    cadeia={'WINE_RELEVANCE': 'PROVED', 'VITICULTURE_RELEVANCE': 'NOT_PROVED'},
    urls=['https://www.foodmakers.it/luca-gardini-the-wine-killer/',
          'https://gardininotes.com/']),

 '@italianwinelover': dict(
    nome='Francesco Saverio Russo', tipo='WINE_MEDIA_CREATOR', regiao='Arezzo, Toscana',
    ocupacao='wine blogger, educador e degustador profissional desde 2006',
    produtor='NOT_PROVED',
    produtor_ev='descreve-se como divulgador; nenhuma titularidade de vinha declarada',
    crop_state='PARTIAL',
    crop_ev='autodescrição "dalla vigna al bicchiere" inclui a vinha, mas o eixo do '
            'canal é o vinho e a audiência é de consumidores. Não é WRONG_ASSIGNMENT '
            '— é relevância parcial que NÃO sustenta ativação agronômica.',
    cadeia={'WINE_RELEVANCE': 'PROVED', 'VITICULTURE_RELEVANCE': 'PARTIAL'},
    seguidores={'INSTAGRAM': 199000},
    urls=['https://www.instagram.com/italianwinelover/',
          'https://vivantwine.com/blogs/brand-ambassador-italianwinelover/francesco-saverio-russo']),

 '@mircocolzani_gardendesigner': dict(
    nome='Mirco Colzani', tipo='OTHER', regiao='Giussano, Monza e Brianza',
    ocupacao='garden designer / paisagista; projeta jardins na Itália, Suíça, '
             'Reino Unido e Austrália; formado pela Scuola Agraria di Minoprio',
    produtor='NOT_PROVED',
    produtor_ev='projeta jardins ornamentais; não há produção agrícola',
    crop_state='WRONG_ASSIGNMENT',
    crop_ev='a seed o atribuiu a FRUTICULTURA. A atividade é design de jardim — '
            'ornamental, não produção de fruta. Erro de categoria, não de grau.',
    cadeia={},
    urls=['https://www.mircocolzanigardens.com/',
          'https://orticolario.it/mirco-colzani/']),

 '@evolovers': dict(
    nome='Leonardo Leggeri', tipo='FARMER_CREATOR', regiao='Puglia',
    ocupacao='produtor de azeite extra virgem; fundador da comunidade Evolovers',
    produtor='PROVED',
    produtor_ev='descrito como PRODUTOR pugliese; a comunidade nasceu em 2020 '
                'partilhando "la vita nei campi" — podas, colheitas e degustações',
    crop_state='PROVED', crops=['OLIVE'],
    crop_ev='podas e colheitas no próprio olival, além de degustação de azeite',
    cadeia={'OLIVE_GROWING_RELEVANCE': 'PROVED', 'OLIVE_OIL_RELEVANCE': 'PROVED'},
    urls=['https://www.cronachedigusto.it/l-intervista/lolio-raccontato-sui-social-cinque-evocreator-bravissimi-da-seguire/'],
    refuta_suspeita=True),

 '@davide_gomiero': dict(
    nome='Davide Gomiero', tipo='FARMER_CREATOR', regiao='Limena, Padova, Veneto',
    ocupacao='agricultor na empresa familiar Azienda Agricola F.lli Gomiero',
    produtor='PROVED',
    produtor_ev='empresa familiar de ~400 ha com ~1.200 bovinos de leite; registro '
                'societário público da Azienda Agricola F.lli Gomiero',
    crop_state='PARTIAL', crops=['MAIZE', 'ALFALFA', 'SOYBEAN', 'FORAGE'],
    crop_ev='fontes declaram feno, MILHO, alfafa e soja para alimentar o rebanho. '
            'A seed alegou TRIGO e ARROZ: milho CONFIRMA a alegação de MAIZE, '
            'trigo e arroz NÃO aparecem em nenhuma fonte.',
    cadeia={},
    seguidores={'INSTAGRAM': 410000},
    audiencia='MIXED',
    audiencia_ev='fonte descreve a comunidade como agricultores, criadores e entusiastas',
    urls=['https://www.greenme.it/ambiente/agricoltura/davide-gomiero-agri-influencer-star-tv/',
          'https://www.italiafruit.net/davide-gomiero-lagri-influencer-che-porta-lagricoltura-in-tv',
          'https://atoka.io/public/it/azienda/azienda-agricola-flli-gomiero-di-gomiero-davide/db50de18436a']),

 '@filippoballardin': dict(
    nome='Filippo Ballardin', tipo='AGRONOMIST_CREATOR', regiao='Veneto',
    ocupacao='criador de conteúdo de divulgação agronômica ("Agronomix", '
             '"L\'agricoltura spiegata facile")',
    produtor='NOT_PROVED',
    produtor_ev='atua como divulgador; nenhuma exploração própria declarada',
    crop_state='NOT_PROVED',
    crop_ev='a seed alegou TRIGO. O conteúdo é divulgação agronômica geral; '
            'nenhuma fonte prova recorte de trigo.',
    cadeia={},
    urls=['https://www.influenxer.it/influencer/i-giovani-che-hanno-riscoperto-lagricoltura-e-i-farm-influencer/']),

 '@agromoderni': dict(
    nome='Agromoderni / Italian Farm', tipo='AG_MEDIA_CREATOR', regiao='Cuneo, Piemonte',
    ocupacao='canal de mídia agrícola no YouTube desde 2011; informação e entretenimento',
    produtor='NOT_PROVED',
    produtor_ev='a fonte o descreve como criador de conteúdo e marca, não como '
                'azienda agricola',
    crop_state='NOT_PROVED',
    crop_ev='a seed alegou TRIGO e ARROZ. Nenhuma fonte prova recorte de cultura. '
            'Cuneo fica no Piemonte, região de arroz — mas geografia não é conteúdo.',
    cadeia={},
    urls=['https://www.youtube.com/user/agromoderni',
          'https://x.com/agromoderni']),

 '@maria.pezone': dict(
    nome='Maria Pezone', tipo='FARMER_CREATOR', regiao='Campania',
    ocupacao='formada em Ciências Agrárias; gere a empresa familiar Egiziaca',
    produtor='PROVED', produtor_ev='gere empresa familiar de 130 ha',
    crop_state='PARTIAL', crops=['LETTUCE', 'MELON'],
    crop_ev='130 ha de alface Iceberg e melão retato. A seed a colocou em '
            'TOMATE/HORTICULTURA: horticultura CONFIRMA, tomate NÃO.',
    cadeia={}, seguidores={'INSTAGRAM': 21000},
    urls=['https://www.cibotoday.it/storie/agricoltura/influencer-agricoltura-italiani-chi-sono.html']),

 '@yuliyapyliavska': dict(
    nome='Yuliya Pyliavska', tipo='MACHINERY_CREATOR', regiao='Vigevano, Lombardia',
    ocupacao='agri-blogger; conteúdo de agricultura e tratores',
    produtor='NOT_KNOWN', produtor_ev='fonte a trata como blogger, sem declarar exploração',
    crop_state='NOT_PROVED',
    crop_ev='a seed alegou MILHO e ARROZ. O conteúdo declarado é agricultura e '
            'tratores. Vigevano fica na Lomellina, cinturão do arroz — mas isso é '
            'geografia, não conteúdo, e não prova cultura.',
    cadeia={}, seguidores={'INSTAGRAM': 109000, 'TIKTOK': 209000},
    urls=['https://www.informatorevigevanese.it/attualita/2023/04/04/news/trecentomila-followers-yuliya-la-blogger-che-parla-di-agricoltura-e-trattori-556068/']),
}


def montar():
    seed = cr.carregar('SEED-IT-CANDIDATES.json')
    porhandle = {r['ORIGIN_ID']: r for r in seed}

    fora, contagem = [], {}
    for handle, m in MEDIDO.items():
        base = porhandle.get(handle)
        if not base:
            print('IGNORADO (não está na seed): %s' % handle); continue
        alegado = base['CROP_CLAIMED_BY_SEED']
        linha = {
            'CREATOR_ID': base['CREATOR_ID'], 'HANDLE': handle,
            'NAME_FROM_SEED': base['NAME'], 'NAME_MEASURED': m['nome'],
            'COUNTRY': 'IT', 'REGION': m['regiao'], 'LANGUAGE': 'it',
            'OCCUPATION': m['ocupacao'], 'CREATOR_TYPE': m['tipo'],
            'ENTITY_KIND': 'PERSON',
            'ACTUAL_FARMER': m['produtor'], 'ACTUAL_FARMER_EVIDENCE': m['produtor_ev'],
            'CROP_CLAIMED_BY_SEED': alegado,
            'CROP_PROVED_BY_CONTENT': m.get('crops', cr.NAO_SEI),
            'CROP_STATE': m['crop_state'], 'CROP_EVIDENCE': m['crop_ev'],
            'CROP_PROOF_URLS': m['urls'],
            'SUSPECTED_BY_HANDLE': base.get('SUSPECTED_CHAIN_MISMATCH'),
            'SUSPICION_OUTCOME': ('REFUTED_BY_EVIDENCE' if m.get('refuta_suspeita')
                                  else ('CONFIRMED' if base.get('SUSPECTED_CHAIN_MISMATCH') == 'YES'
                                        and m['crop_state'] in ('WRONG_ASSIGNMENT', 'PARTIAL')
                                        else 'NOT_APPLICABLE')),
            'FOLLOWERS_BY_PLATFORM': m.get('seguidores', cr.NAO_SEI),
            'AUDIENCE_TYPE': m.get('audiencia', 'NOT_KNOWN'),
            'AUDIENCE_EVIDENCE': m.get('audiencia_ev', cr.NAO_SEI),
            'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN',
            'ADAMA_COLLABORATION_OBSERVED': 'NOT_OBSERVED',
            'ACTIVITY_STATE': 'NOT_MEASURED',
            'IDENTITY_STATE': 'PROVED',
            'IDENTITY_EVIDENCE': 'nome, ocupação e atividade confirmados por %d fonte(s) '
                                 'independente(s) da seed' % len(m['urls']),
            'SOURCE_KIND': 'SEARCH_SUMMARY_NOT_OPENED',
            'COLLECTION_ROUTE': ROTA, 'CAPTURE_DATE': CAPTURA,
        }
        for c in ('WINE_RELEVANCE', 'VITICULTURE_RELEVANCE',
                  'OLIVE_OIL_RELEVANCE', 'OLIVE_GROWING_RELEVANCE'):
            linha[c] = (m.get('cadeia') or {}).get(c, 'NOT_KNOWN')
        contagem[m['crop_state']] = contagem.get(m['crop_state'], 0) + 1
        fora.append(linha)

    produtores = [x for x in fora if x['ACTUAL_FARMER'] == 'PROVED']
    errados = [x for x in fora if x['CROP_STATE'] == 'WRONG_ASSIGNMENT']
    refutadas = [x for x in fora if x['SUSPICION_OUTCOME'] == 'REFUTED_BY_EVIDENCE']

    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA, 'COLLECTION_ROUTE': ROTA,
        'LAW': 'Este arquivo guarda a MEDIÇÃO. SEED-IT-CANDIDATES.json guarda a '
               'ALEGAÇÃO e não é sobrescrito — senão a taxa de erro da seed se perde.',
        'SEED_UNIQUE_HANDLES': len(seed),
        'VALIDATED_THIS_ROUND': len(fora),
        'NOT_YET_VALIDATED': len(seed) - len(fora),
        'CROP_STATE_COUNT': contagem,
        'ACTUAL_FARMER_PROVED': len(produtores),
        'WRONG_ASSIGNMENT': len(errados),
        'SUSPICION_REFUTED_BY_EVIDENCE': len(refutadas),
        'SUSPICION_NOTE':
            'A suspeita lexical errou em %d caso(s). Por isso ela nunca promove '
            'sozinha a WRONG_ASSIGNMENT: um portão que confiasse nela teria '
            'descartado um olivicultor real pelo nome do handle.' % len(refutadas),
        'VALIDATIONS': fora,
    }
    with open(os.path.join(cr.BASE, 'SEED-IT-VALIDATION.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/SEED-IT-VALIDATION.json')
    print('VALIDADOS=%d de %d  PRODUTORES_PROVADOS=%d  WRONG_ASSIGNMENT=%d  SUSPEITA_REFUTADA=%d'
          % (len(fora), len(seed), len(produtores), len(errados), len(refutadas)))
    for k, v in sorted(contagem.items()):
        print('  CROP_STATE %-18s %d' % (k, v))


if __name__ == '__main__':
    montar()
