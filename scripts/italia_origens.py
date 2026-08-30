#!/usr/bin/env python3
"""
ITALY-ORIGIN-UNIVERSE — quem existe, em que camada, e por que foi selecionado.

Uma origem NÃO é um perfil social. É qualquer entidade que **produz conteúdo público
verificável** sobre a agricultura italiana: pesquisador, técnico, serviço público,
cooperativa, mídia, empresa. Misturar as classes é o erro que a Espanha pagou caro — ali
`46 % das origens do LinkedIn eram páginas de empresa` posando de pessoas.

REGRAS QUE ESTE ARQUIVO EXERCE

  · `ORIGIN ≠ CHANNEL ≠ CONTENT`. Uma pessoa em três plataformas é UMA origem com três
    evidências. Nunca se somam.
  · **`ROLE_EVIDENCE` é obrigatório.** Papel sem evidência estruturada é papel inventado.
    Nenhuma origem entra aqui com papel deduzido de prosa livre.
  · **`SELECTION_REASON` é obrigatório.** Se não dá para escrever por que a origem entrou,
    ela entrou por cota — e cota não é critério.
  · `SOURCE_GEOGRAPHY ≠ FACT_GEOGRAPHY`. A sede da organização não é a região do fato.
  · **Seguidor não é campo deste dataset.** `FOLLOWERS ≠ AUTHORITY`, e a forma mais segura
    de não usar alcance como autoridade é não guardar alcance junto da autoridade.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = os.path.join(ROOT, 'data', 'samples')
DEST = os.path.join(S, 'IT-ORIGENS', 'ITALY-ORIGIN-UNIVERSE.json')

NAO_SEI = 'NÃO SEI'


def _ler(rel):
    p = os.path.join(S, rel)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def institucionais():
    """Origens institucionais medidas nesta e nas rodadas anteriores."""
    return [
        {'ORIGIN_ID': 'IT-ORG-VENETO-FITO', 'TYPE': 'PUBLIC_INSTITUTION',
         'NAME': 'Regione del Veneto — U.O. Fitosanitario', 'REGION': 'Veneto',
         'ROLE': 'REGIONAL_PHYTOSANITARY_SERVICE',
         'ROLE_EVIDENCE': 'emite decreto de lotta obbligatoria (DDR 13645/2026) e bollettini semanais',
         'CROPS': ['Videira', 'Oliveira', 'Frutícolas', 'Hortícolas', 'Trigo', 'Beterraba'],
         'ISSUES': ['Flavescência dourada', 'Bactrocera oleae', 'Cercospora beticola'],
         'CHANNELS': ['https://www.regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026'],
         'PUBLIC_CONTENT': '2026: 28 olivo · 25 frutícola · 21 hortícola · 16+ vite · 2 erbacee',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'fonte do sinal corrente dos casos IT-HERO-001 e IT-DEMO-001'},
        {'ORIGIN_ID': 'IT-ORG-LOMBARDIA-SFR', 'TYPE': 'PUBLIC_INSTITUTION',
         'NAME': 'Regione Lombardia — Servizio Fitosanitario Regionale', 'REGION': 'Lombardia',
         'ROLE': 'REGIONAL_PHYTOSANITARY_SERVICE',
         'ROLE_EVIDENCE': 'Comunicato Giunta 25/05/2026 n. 39 (BURL) com as datas obrigatórias',
         'CROPS': ['Videira', 'Macieira'], 'ISSUES': ['Flavescência dourada'],
         'CHANNELS': ['https://www.fitosanitario.regione.lombardia.it/'],
         'PUBLIC_CONTENT': '2026: 6 vite · 4 melo · nenhum de milho',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'define a janela obrigatória e o critério de elegibilidade de produto'},
        {'ORIGIN_ID': 'IT-ORG-ERSA-FVG', 'TYPE': 'PUBLIC_INSTITUTION',
         'NAME': 'ERSA — Servizio fitosanitario e chimico, Friuli-Venezia Giulia',
         'REGION': 'Friuli-Venezia Giulia', 'ROLE': 'REGIONAL_PHYTOSANITARY_SERVICE',
         'ROLE_EVIDENCE': 'publica a única série de boletim de MILHO medida na Itália',
         'CROPS': ['Milho', 'Soja', 'Trigo', 'Cevada', 'Colza'],
         'ISSUES': ['Piralide (Ostrinia nubilalis)', 'Diabrotica virgifera'],
         'CHANNELS': ['http://difesafitosanitaria.ersa.fvg.it/'],
         'PUBLIC_CONTENT': '10 boletins de MAIS em 2026; último n.15 de 12/08 com BBCH e limiar',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'fonte do sinal corrente do caso IT-HERO-002'},
        {'ORIGIN_ID': 'IT-ORG-CONSFITO-PC', 'TYPE': 'PUBLIC_INSTITUTION',
         'NAME': 'Consorzio Fitosanitario Provinciale di Piacenza',
         'REGION': 'Emilia-Romagna (Piacenza)', 'ROLE': 'PROVINCIAL_PHYTOSANITARY_CONSORTIUM',
         'ROLE_EVIDENCE': ('declara-se coordenado pelo Servizio Fitosanitario Regionale; '
                           'publica bollettini territoriali, monitoraggi e modelli previsionais'),
         'CROPS': ['Milho', 'Videira', 'Tomate'], 'ISSUES': ['Diabrotica virgifera virgifera'],
         'CHANNELS': ['https://www.fitosanitario.pc.it/diabrotica-del-mais/'],
         'PUBLIC_CONTENT': 'página dedicada à diabrotica; bollettini NÃO obtidos (sem PDF no HTML lido)',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': ('nó de rede técnica na 4ª região de milho — a rota de boletim '
                              'fica NOT_OBTAINED, não inexistente')},
        {'ORIGIN_ID': 'IT-ORG-CREA', 'TYPE': 'RESEARCH_INSTITUTION',
         'NAME': 'CREA — Cerealicoltura e Colture Industriali', 'REGION': 'Nacional',
         'ROLE': 'NATIONAL_RESEARCH_BODY',
         'ROLE_EVIDENCE': 'organiza a Giornata del Mais e publica gravação e apresentações',
         'CROPS': ['Milho'], 'ISSUES': ['Micotoxina', 'Nutrição nitrogenada'],
         'CHANNELS': ['https://www.crea.gov.it/web/cerealicoltura-e-colture-industriali/'],
         'PUBLIC_CONTENT': ('Giornata del Mais 2026 (Kilometro Rosso, Bergamo) — micotoxinas, '
                            'rede nacional de comparação varietal; gravação pública'),
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': ('evento técnico público sobre o cluster científico dominante do '
                              'milho italiano (208 trabalhos em micotoxina)')},
        {'ORIGIN_ID': 'IT-ORG-FMACH', 'TYPE': 'RESEARCH_INSTITUTION',
         'NAME': 'Fondazione Edmund Mach', 'REGION': 'Trentino',
         'ROLE': 'RESEARCH_AND_EXTENSION',
         'ROLE_EVIDENCE': 'portal fitoemergenze com página dedicada à flavescência dourada',
         'CROPS': ['Videira'], 'ISSUES': ['Flavescência dourada'],
         'CHANNELS': ['https://fitoemergenze.fmach.it/flavescenza-dorata'],
         'PUBLIC_CONTENT': 'material técnico de emergência fitossanitária; bollettini de difesa integrata',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'explicação técnica pública sobre o issue do IT-HERO-001'},
        {'ORIGIN_ID': 'IT-ORG-COPROB', 'TYPE': 'COOPERATIVE',
         'NAME': 'Co.Pro.B. — Cooperativa Produttori Bieticoli', 'REGION': 'Norte (multi)',
         'ROLE': 'PRODUCER_COOPERATIVE_WITH_DSS',
         'ROLE_EVIDENCE': ('o boletim oficial do Vêneto cita o DSS de Cercospora da Co.Pro.B. '
                           'como fonte de limiar — cooperativa que PRODUZ sinal de campo'),
         'CROPS': ['Beterraba açucareira'], 'ISSUES': ['Cercospora beticola'],
         'CHANNELS': ['https://www.coprob.com/'],
         'PUBLIC_CONTENT': 'DSS citado por serviço público; site devolveu 202 nesta sondagem',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'único caso medido de cooperativa cujo sinal é citado por órgão oficial'},
        {'ORIGIN_ID': 'IT-ORG-ASSOPROLI', 'TYPE': 'PRODUCER_ORG',
         'NAME': 'Assoproli Bari', 'REGION': 'Puglia', 'ROLE': 'PRODUCER_ORGANISATION',
         'ROLE_EVIDENCE': 'publica bollettini fitosanitari de mosca-da-azeitona',
         'CROPS': ['Oliveira'], 'ISSUES': ['Bactrocera oleae'],
         'CHANNELS': ['https://www.assoproli.it/bollettini-fitosanitari/'],
         'PUBLIC_CONTENT': 'boletins expostos em HTML alcançável datados de 2024',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': ('assume o sinal de campo que a região deixou de publicar em 2018 — '
                              'a Puglia tem 31,2 % da oliveira italiana')},
        {'ORIGIN_ID': 'IT-ORG-TERRAEVITA', 'TYPE': 'TECHNICAL_MEDIA',
         'NAME': 'Terra e Vita (Edagricole)', 'REGION': 'Nacional', 'ROLE': 'TRADE_MEDIA',
         'ROLE_EVIDENCE': 'RSS ativo, 30 itens, mais recente 29/08/2026',
         'CROPS': ['Vários'], 'ISSUES': ['Vários'],
         'CHANNELS': ['https://terraevita.edagricole.it/feed/'],
         'PUBLIC_CONTENT': 'medido: perfil MARKET_AND_POLICY — preço, geopolítica, subsídio, DOP',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': ('mede atenção de mercado e política. NÃO mede campo — '
                              'MEDIA_SIGNAL ≠ FIELD_SIGNAL')},
        {'ORIGIN_ID': 'IT-ORG-AGRONOTIZIE', 'TYPE': 'TECHNICAL_MEDIA',
         'NAME': 'AgroNotizie (Image Line)', 'REGION': 'Nacional', 'ROLE': 'TECHNICAL_MEDIA',
         'ROLE_EVIDENCE': 'perfil de assunto medido como FIELD_OR_TECHNICAL',
         'CROPS': ['Vários'], 'ISSUES': ['Defesa e diserbo'],
         'CHANNELS': ['https://agronotizie.imagelinenetwork.com/'],
         'PUBLIC_CONTENT': 'acesso intermitente — 403 numa sondagem, 200 noutra, no mesmo dia',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'única mídia com perfil técnico entre as medidas'},
        {'ORIGIN_ID': 'IT-ORG-INFORMATORE', 'TYPE': 'TECHNICAL_MEDIA',
         'NAME': "L'Informatore Agrario", 'REGION': 'Nacional', 'ROLE': 'TRADE_MEDIA',
         'ROLE_EVIDENCE': 'RSS ativo, 10 itens', 'CROPS': ['Vários'], 'ISSUES': ['Vários'],
         'CHANNELS': ['https://www.informatoreagrario.it/feed/'],
         'PUBLIC_CONTENT': 'perfil MARKET_AND_POLICY',
         'IDENTITY_STATUS': 'INSTITUTIONAL_CONFIRMED',
         'SELECTION_REASON': 'segunda mídia técnica nacional com rota estruturada aberta'},
    ]


def concorrentes():
    """Sinal público de concorrente, restrito aos crop×issue dos casos."""
    return [
        {'ORIGIN_ID': 'IT-COMP-SYNGENTA', 'TYPE': 'COMPANY', 'NAME': 'Syngenta Italia',
         'ROLE': 'COMPETITOR', 'REGION': 'Nacional',
         'SIGNAL_TYPE': 'TECHNICAL_CONTENT',
         'SIGNAL': 'página "Piralide e Diabrotica: conoscerli per controllarli"',
         'CROP': 'Milho', 'ISSUE': 'Piralide / Diabrotica',
         'RELATES_TO_CASE': 'IT-HERO-002',
         'ACCESS': 'BLOCKED — 403 do site; existência confirmada por índice de busca',
         'IDENTITY_STATUS': 'COMPANY_CONFIRMED',
         'NOT_INFERRED': ['estratégia', 'vendas', 'prioridade interna', 'market share']},
        {'ORIGIN_ID': 'IT-COMP-BAYER', 'TYPE': 'COMPANY', 'NAME': 'Bayer Crop Science Italia',
         'ROLE': 'COMPETITOR', 'REGION': 'Nacional',
         'SIGNAL_TYPE': 'TECHNICAL_CONTENT',
         'SIGNAL': ('Agricampus — "Scaphoideus titanus: come evitare la flavescenza dorata", '
                    'em 10 passos'),
         'CROP': 'Videira', 'ISSUE': 'Flavescência dourada / Scaphoideus titanus',
         'RELATES_TO_CASE': 'IT-HERO-001',
         'ACCESS': 'BLOCKED — 403 do site; existência confirmada por índice de busca',
         'IDENTITY_STATUS': 'COMPANY_CONFIRMED',
         'NOT_INFERRED': ['estratégia', 'vendas', 'prioridade interna', 'market share']},
        {'ORIGIN_ID': 'IT-COMP-CORTEVA', 'TYPE': 'COMPANY', 'NAME': 'Corteva Italia',
         'ROLE': 'COMPETITOR', 'REGION': 'Nacional', 'SIGNAL_TYPE': 'PUBLIC_SITE',
         'SIGNAL': 'site acessível; perfil de assunto medido como FIELD_OR_TECHNICAL',
         'CROP': NAO_SEI, 'ISSUE': NAO_SEI, 'RELATES_TO_CASE': NAO_SEI,
         'ACCESS': 'GREEN', 'IDENTITY_STATUS': 'COMPANY_CONFIRMED',
         'NOT_INFERRED': ['estratégia', 'vendas', 'prioridade interna', 'market share']},
        {'ORIGIN_ID': 'IT-COMP-BASF', 'TYPE': 'COMPANY', 'NAME': 'BASF Agro Italia',
         'ROLE': 'COMPETITOR', 'REGION': 'Nacional', 'SIGNAL_TYPE': 'PUBLIC_SITE',
         'SIGNAL': 'site acessível; perfil MARKET_AND_POLICY no que foi lido',
         'CROP': NAO_SEI, 'ISSUE': NAO_SEI, 'RELATES_TO_CASE': NAO_SEI,
         'ACCESS': 'GREEN', 'IDENTITY_STATUS': 'COMPANY_CONFIRMED',
         'NOT_INFERRED': ['estratégia', 'vendas', 'prioridade interna', 'market share']},
    ]


def creators_rejeitados():
    """A rota de descoberta que FALHOU no gate, com o número que a reprovou."""
    return {
        'ROUTE': 'YouTube — descoberta por "principais canais de agricultura italiana"',
        'CHANNELS_TESTED': 4, 'VIDEOS_SAMPLED': 60,
        'CROP_OR_ISSUE_RELEVANT': 4, 'RELEVANCE_RATE_PCT': 6.7,
        'DETAIL': [
            {'CHANNEL': 'Edagricole', 'RELEVANT': '1/15', 'LAST': '2026-08-28',
             'CONTENT': 'testes de tratores (New Holland, Massey Ferguson)'},
            {'CHANNEL': 'Consorzi Agrari d\'Italia', 'RELEVANT': '1/15', 'LAST': '2025-11-13',
             'CONTENT': 'institucional; canal parado há 9 meses'},
            {'CHANNEL': 'AgroNotizie', 'RELEVANT': '1/15', 'LAST': '2026-07-23',
             'CONTENT': 'solo, financiamento, agrivoltaico'},
            {'CHANNEL': 'Agri Italia', 'RELEVANT': '5/15', 'LAST': '2015-03-04',
             'CONTENT': 'canal morto desde 2015; "relevância" veio de "prova in campo" de máquina'},
        ],
        'VERDICT': 'REJECTED',
        'WHY': ('6,7 % de relevância a CROP×ISSUE. São canais de MÁQUINA e de NEGÓCIO, não '
                'vozes técnicas agronômicas, e dois estão parados. Escalar esta rota '
                'produziria volume sem inteligência.'),
        'WHAT_REPLACES_IT': ('a rota inversa, que a missão já prescrevia: CROP × REGION × '
                             'TOPIC → conteúdo → pessoa. Ela devolveu, em duas buscas, o '
                             'Consorzio de Piacenza, a FMach, a Giornata del Mais do CREA e '
                             'o conteúdo técnico de dois concorrentes — todos ligados aos '
                             'issues dos casos.'),
        'ROUTE_STATUS_YOUTUBE_RSS': ('FUNCIONA sem chave de API — 15 itens por canal, com '
                                     'data e ID. O gargalo é DISCOVERY, não coleta.'),
    }


def main():
    origens = institucionais()
    comps = concorrentes()
    pesq = _ler('IT-T5-001/ITALY-RESEARCHER-UNIVERSE.json')

    por_tipo = {}
    for o in origens + comps:
        por_tipo[o['TYPE']] = por_tipo.get(o['TYPE'], 0) + 1

    out = {
        'DATASET': 'ITALY-ORIGIN-UNIVERSE', 'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-ORIGINS',
        'SOURCE': ('sondagem de fontes IT-SOURCE-PROBE, decretos regionais, boletins de '
                   'campo e busca dirigida por CROP×ISSUE'),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'CONTRACT': {
            'ORIGIN_vs_CHANNEL_vs_CONTENT': 'entidades distintas; nunca somadas',
            'ROLE_EVIDENCE': 'obrigatório — papel sem evidência é papel inventado',
            'SELECTION_REASON': 'obrigatório — origem sem razão entrou por cota',
            'FOLLOWERS': 'não é campo deste dataset, de propósito',
            'GEOGRAPHY': 'SOURCE_GEOGRAPHY ≠ FACT_GEOGRAPHY',
        },
        'BY_TYPE': por_tipo,
        'INSTITUTIONAL_ORIGINS': origens,
        'COMPETITOR_SIGNALS': comps,
        'RESEARCHER_UNIVERSE': (
            {'STATUS': 'BUILT', 'FILE': 'IT-T5-001/ITALY-RESEARCHER-UNIVERSE.json',
             'TOTAL': pesq.get('UNIVERSE_TOTAL'), 'WITH_ORCID': pesq.get('WITH_ORCID')}
            if pesq else {'STATUS': 'PENDING — build em curso'}),
        'FARMER_CREATOR_LAYER': creators_rejeitados(),
        'WHAT_IS_MISSING': [
            'produtores individuais com conteúdo público — não iniciado',
            'creators verificados por CROP×ISSUE — rota de descoberta trocada, não reexecutada',
            'canais sociais dos pesquisadores — camada seguinte',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('origens institucionais %d · concorrentes %d' % (len(origens), len(comps)))
    print('por tipo:', por_tipo)
    print('creators:', out['FARMER_CREATOR_LAYER']['VERDICT'],
          '(%.1f%% de relevância)' % out['FARMER_CREATOR_LAYER']['RELEVANCE_RATE_PCT'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
