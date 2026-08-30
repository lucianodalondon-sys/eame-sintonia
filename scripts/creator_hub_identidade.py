#!/usr/bin/env python3
"""
IDENTIDADE OFICIAL DOS HUBS (§6) — o portão gratuito antes de qualquer raspagem.

    python3 scripts/creator_hub_identidade.py

POR QUE ESTA FASE EXISTE
--------------------------
`nome de feira != handle`. Esta missão já mediu quatro vezes o preço de inferir
endereço a partir de nome — e uma quinta vez na própria rodada 4, quando eu
inferi `youtube.com/@DavidForge` e a fonte mostrou que o canal se chama **La
Chaîne Agricole**.

Por isso `HUB_DISCOVERY` só fica `ENABLED` para hub cuja conta oficial foi
**mostrada por uma fonte**. Hub sem conta provada não é raspado — fica
`ACCOUNT_NOT_RESOLVED`, que é um estado, não uma falha.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'

HUBS = [
 dict(hub='Premios AgroInfluye', pais='ES', tier=1,
      site='https://premiosagroinfluye.com/',
      contas=[dict(plataforma='INSTAGRAM', handle='@agroinfluye',
                   url='https://www.instagram.com/agroinfluye/')],
      fonte='conta nomeada em resultado de busca sobre o prêmio; raspada com sucesso',
      estado='ACCOUNT_RESOLVED', descoberta='ENABLED',
      nota='já rendeu 23 pessoas em 12 publicações'),

 dict(hub='Fieragricola (Verona)', pais='IT', tier=1,
      site='https://www.fieragricola.it/',
      contas=[dict(plataforma='INSTAGRAM', handle='@fieragricolavr',
                   url='https://www.instagram.com/fieragricolavr/'),
              dict(plataforma='FACEBOOK', handle='Fieragricola',
                   url='https://www.facebook.com/Fieragricola/'),
              dict(plataforma='X', handle='@fieragricola',
                   url='https://x.com/fieragricola')],
      fonte='conta oficial nomeada em resultado de busca, com ~23 mil seguidores',
      estado='ACCOUNT_RESOLVED', descoberta='ENABLED',
      nota='não raspada nesta rodada — a rodada priorizou CROP_PROOF'),

 dict(hub='SIVAL (Angers)', pais='FR', tier=1,
      site='https://www.sival-angers.com/',
      contas=[dict(plataforma='INSTAGRAM', handle='@sivalangers',
                   url='https://www.instagram.com/sivalangers/'),
              dict(plataforma='LINKEDIN', handle='sival-angers',
                   url='https://www.linkedin.com/company/sival-angers/')],
      fonte='conta oficial nomeada em resultado de busca (1.316 seguidores, 314 posts)',
      estado='ACCOUNT_RESOLVED', descoberta='ENABLED',
      nota='conta pequena — rendimento provável baixo, testar antes de investir'),

 dict(hub='EIMA International', pais='IT', tier=2,
      site='https://www.eima.it/',
      contas=[dict(plataforma='INSTAGRAM', handle='@eima_international',
                   url='https://www.instagram.com/eima_international/')],
      fonte='URL de publicação da conta oficial apareceu em resultado de busca',
      estado='ACCOUNT_RESOLVED', descoberta='ENABLED',
      nota='RECLASSIFICADO — ver EIMA_SOCIAL_AWARDS abaixo'),

 dict(hub='Enovitis in Campo', pais='IT', tier=1,
      site='https://www.unioneitalianavini.it/',
      contas=[],
      contas_resolvidas=[dict(plataforma='INSTAGRAM', handle='@enovitis_',
                              url='https://www.instagram.com/enovitis_/')],
      fonte='RESOLVIDA NA SEGUNDA TENTATIVA, e sem adivinhar: a conta oficial da '
            'Fieragricola (@fieragricolavr) mencionou @enovitis_ nas proprias '
            'legendas. Uma porta provada abriu a outra — que e exatamente o que o '
            'portao de identidade deveria produzir.',
      estado='ACCOUNT_MENTIONED_NOT_RESOLVED', descoberta='BLOCKED',
      nota_resolucao='A raspagem de @enovitis_ NAO devolveu perfil. A mencao deu um '
                     'CANDIDATO de handle; a resolucao nao o confirmou. Mencao != '
                     'conta existente, e o estado guarda a diferenca.',
      nota='hub tecnicamente excelente (6.500 visitantes, viticultores e agrónomos, '
           'agroquímicos em demonstração) e mesmo assim BLOQUEADO: sem conta provada '
           'não se raspa. Resolver a conta é a próxima ação italiana.'),

 dict(hub='SITEVI (Montpellier)', pais='FR', tier=1,
      site='https://www.sitevi.com/',
      contas=[],
      fonte='NENHUMA — a busca não devolveu conta oficial',
      estado='ACCOUNT_NOT_RESOLVED', descoberta='BLOCKED',
      nota='+1.000 expositores e ~55.000 visitantes profissionais; alto potencial, '
           'conta por resolver'),

 dict(hub='Innov-Agri', pais='FR', tier=1, site=cr.NAO_SEI, contas=[],
      fonte='não pesquisado nesta rodada', estado='NOT_TESTED', descoberta='BLOCKED',
      nota=''),
 dict(hub="Espoirs de l'influence agricole / Les Blacks Moutons", pais='FR', tier=1,
      site='https://www.lesblacksmoutons.com/concours-2025-espoirs-influence-agricole/',
      contas=[],
      fonte='site do concurso nomeado em resultado de busca; conta social não resolvida',
      estado='SITE_RESOLVED_ACCOUNT_NOT', descoberta='BLOCKED',
      nota="4a edicao em 2026; premia por crescimento de seguidores por rede; "
           "entrega de premios no Salon de l'Agriculture; vencedores ganham um ano "
           "de SYRPA. Juri inclui creator de PECUARIA — atencao ao recorte."),
 dict(hub='FederUnacoma / AGIA-CIA', pais='IT', tier=1, site=cr.NAO_SEI, contas=[],
      fonte='não pesquisado nesta rodada', estado='NOT_TESTED', descoberta='BLOCKED',
      nota=''),
]

# §7 · a reclassificação medida
RECLASSIFICACAO = [
 dict(hub='EIMA Social Awards', antes='MASTER_CREATOR_SOURCE',
      depois='BRAND_EXHIBITOR_COMMUNICATION_HUB',
      motivo='a fonte declara que o prémio foi criado em 2024 para premiar as '
             'EMPRESAS que se destacam na promoção da própria participação na feira '
             'nas redes sociais. Premia expositor, não creator.',
      continua_util_para=['brand activation', 'campaign discovery',
                          'agri communication actors'],
      url='https://www.eima.it/it/comunicati-stampa-fiera-macchine-agricole-giardinaggio.php'),
]

# §9 · a agência como porta
INTERMEDIARIOS = [
 dict(nome='Wonderland Agency', pais='FR',
      url='https://www.wonderland-agency.fr/',
      fundadora='Émilie Vivier-Houvet',
      registo='sociedade registada em Itteville (91760), SIREN 821377579',
      linkedin='https://www.linkedin.com/in/emilie-vivier-houvet-b4985b3b/',
      atividade_agri='a fundadora atua como consultora de social media e influência e '
                     'GERE PARCERIAS de influenciadores agrícolas; é referência em '
                     'eventos agrícolas por propor farmer-influencers a salões '
                     'profissionais como SITEVI',
      identidade='PROVED',
      classificacao='CREATOR_INTERMEDIARY_HUB',
      creators_representados='NOT_RECOVERED — nenhuma lista pública de talentos '
                             'agrícolas foi encontrada nesta rodada',
      contato_publico='site oficial e LinkedIn da fundadora',
      aviso='NÃO assumir que todo talento da agência é agrícola. A agência declara '
            'acompanhar PME em transformação digital em geral.',
      fontes=['https://www.wonderland-agency.fr/',
              'https://www.societe.com/societe/wonderland-agency-821377579.html',
              'https://ajcam.org/adherents/emilie-vivier-houvet/']),
]


def montar():
    from collections import Counter
    for h in HUBS:
        h['HUB_ID'] = 'HUBID-%s-%s' % (h['pais'], h['hub'][:18].replace(' ', '_'))
        h['CAPTURE_DATE'] = CAPTURA
    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'LAW': 'nome de feira != handle. HUB_DISCOVERY só fica ENABLED para hub cuja '
               'conta oficial foi MOSTRADA por uma fonte. Sem conta provada, não se '
               'raspa — ACCOUNT_NOT_RESOLVED é estado, não falha.',
        'PRECEDENTE': 'nesta mesma rodada eu inferi youtube.com/@DavidForge a partir do '
                      'nome; a fonte mostrou que o canal se chama "La Chaîne Agricole".',
        'HUBS_TESTED': len(HUBS),
        'BY_STATE': dict(Counter(h['estado'] for h in HUBS)),
        'DISCOVERY_ENABLED': [h['hub'] for h in HUBS if h['descoberta'] == 'ENABLED'],
        'DISCOVERY_BLOCKED': [h['hub'] for h in HUBS if h['descoberta'] == 'BLOCKED'],
        'HUBS': HUBS,
        'RECLASSIFIED': RECLASSIFICACAO,
        'INTERMEDIARIES': INTERMEDIARIOS,
    }
    with open(os.path.join(cr.BASE, 'HUB-OFFICIAL-IDENTITY.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: HUB-OFFICIAL-IDENTITY.json')
    print('TESTADOS=%d  %s' % (len(HUBS), corpo['BY_STATE']))
    print('DESCOBERTA LIBERADA:', corpo['DISCOVERY_ENABLED'])
    print('DESCOBERTA BLOQUEADA:', corpo['DISCOVERY_BLOCKED'])
    print('RECLASSIFICADO: EIMA Social Awards -> BRAND_EXHIBITOR_COMMUNICATION_HUB')
    print('INTERMEDIARIO PROVADO: Wonderland Agency (FR)')


if __name__ == '__main__':
    montar()
