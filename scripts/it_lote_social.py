#!/usr/bin/env python3
"""
LOTE CONGELADO ITALIA — as contas sociais que a rota do Sintonia Scrap deve visitar.

    py scripts/it_lote_social.py

POR QUE UM LOTE, E POR QUE CONGELADO
--------------------------------------
A ordem que a Missao 14 provou e lei aqui tambem:

    LOTE CONGELADO -> PERFIL -> OBJETO -> (so entao) ROTA PAGA

Se a lista muda entre a coleta e a medicao, o rendimento fica medido contra um
denominador que se mexeu. Criterio novo produz V2 explicita, com a V1 preservada.

O CRITERIO DE ENTRADA, E POR QUE ELE E ESTREITO
-------------------------------------------------
    ACCOUNT_IDENTITY_STATE = DECLARED_BY_THE_ORGANISATION

Cada handle desta lista foi lido no SITE da propria organizacao, em 2026-09-03, e o
arquivo de prova diz em qual leitura. Handle achado por busca livre NAO ENTRA — foi
exatamente a identidade ausente que reprovou a coleta espanhola de Instagram
(`ES-T8-003`, FAILED_WITH_REASON: 24 de 32 contas nao declaravam pais).

    O ACERVO CANONICO DA ITALIA TEM ZERO PERFIL INSTAGRAM E ZERO LINKEDIN.
    Este lote e a primeira lista italiana com identidade provada.

O QUE ESTE ARQUIVO NAO FAZ
----------------------------
Nao coleta. Nao paga. Nao decide janela. Ele congela QUEM visitar e POR QUE cada conta
merece a visita. A coleta e do `sintonia-scrap.yml`, na maquina que tem navegador e
nucleos — e esta sessao NAO tem: o Chrome nao atravessa o proxy (ERR_CONNECTION_RESET
em todo host) e a pagina de perfil do Instagram redireciona para login (HTTP 302).

    ROTA BLOQUEADA PARA ESTA SESSAO != ROTA INEXISTENTE.
    A rota de EMBED de POST respondeu HTTP 200 com 628 KB daqui. Falta o shortcode,
    que so a passada de perfil entrega.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'COMPETITOR-PUBLIC-COMM')
CAPTURA = '2026-09-03'


def C(handle, org, papel, plataforma, prova, razao, crops, prioridade):
    """PAGE_ROLE separa o que a Espanha misturou: tres funcionarios de FMC, UPL e BASF
    foram contados como se fossem o canal da empresa porque o headline nomeava o
    empregador. PAPEL E DA CONTA, NUNCA DO CONTEUDO."""
    return {
        'HANDLE': handle,
        'URL': {'INSTAGRAM': 'https://www.instagram.com/%s/' % handle,
                'LINKEDIN': 'https://www.linkedin.com/%s' % handle,
                'YOUTUBE': 'https://www.youtube.com/%s' % handle}[plataforma],
        'PLATFORM': plataforma,
        'ORGANISATION': org,
        'PAGE_ROLE': papel,
        'ACCOUNT_IDENTITY_STATE': 'DECLARED_BY_THE_ORGANISATION',
        'IDENTITY_EVIDENCE': prova,
        'COUNTRY_SCOPE': 'LOCAL_COUNTRY_PROVED',
        'ADAMA_RELEVANCE_REASON': razao,
        'CROPS_RELEVANT': crops,
        'COLLECTION_PRIORITY': prioridade,
    }


CONTAS = [
    # ── PRIORIDADE 1 · quem observa campo nas culturas de maior peso de rotulo ──
    C('ersa_fvg_informa', 'ERSA — Agenzia regionale sviluppo rurale FVG', 'PUBLIC_BODY', 'INSTAGRAM',
      'declarado em difesafitosanitaria.ersa.fvg.it / ersa.fvg.it (leitura 2026-09-03)',
      'e o mesmo servico que assina os bollettini de melo do Friuli-Venezia Giulia — a regiao '
      'declarada de OPP_9C600748BB1B (mais x piralide) e OPP_F139E05A9F3A (pomodoro x oidio)',
      ['MELO', 'MAIS', 'VITE', 'SOIA'], 1),
    C('agralia.it', 'Agralia Studio Agronomico (Brescia)', 'TECHNICAL_ADVISORY', 'INSTAGRAM',
      'declarado em agralia.it, junto do feed e do canal YouTube (leitura 2026-09-03)',
      'estudio agronomico privado que publica bollettino proprio de vite na Lombardia — voz '
      'tecnica que aconselha o produtor, camada que o acervo italiano nao tem',
      ['VITE', 'OLIVO', 'MAIS'], 1),
    C('aipp_protezione_piante', 'AIPP — Associazione Italiana per la Protezione delle Piante',
      'SCIENTIFIC_SOCIETY', 'INSTAGRAM',
      'declarado em aipp.it (leitura 2026-09-03)',
      'sociedade cientifica italiana da protecao das plantas — o proprio negocio da ADAMA',
      ['TODAS'], 1),
    C('agrintesa_ortofrutta_vino', 'Agrintesa Soc. Coop. Agricola', 'COOPERATIVE', 'INSTAGRAM',
      'declarado em agrintesa.it (leitura 2026-09-03)',
      'cooperativa da Romagna nas pomacee — mesma area de OPP_20D89B04F64D e OPP_DA4B5954F72A '
      'e da rede de trappole da cimice',
      ['MELO', 'PERO', 'PESCO', 'ACTINIDIA', 'VITE'], 1),
    C('fmc_agro_italia', 'FMC Agro Italia', 'COMPANY', 'INSTAGRAM',
      'declarado em ag.fmc.com/it (leitura 2026-09-03)',
      'primeiro canal social italiano de concorrente com identidade declarada pela propria '
      'empresa — o acervo tem o site, nao o canal',
      ['VITE', 'MAIS', 'POMODORO', 'FRUMENTO'], 1),

    # ── PRIORIDADE 2 · ciencia e agromet que sustentam janela ──
    C('fondazionemach', 'Fondazione Edmund Mach (FEM/CTT)', 'RESEARCH_INSTITUTION', 'INSTAGRAM',
      'declarado em fmach.it e ctt.fmach.it (leitura 2026-09-03)',
      'o CTT assina os bollettini de difesa integrata do Trentino, regiao de OPP_75C37DED9160 '
      '(melo x carpocapsa) e das crop windows de melo',
      ['MELO', 'VITE'], 2),
    C('crearicerca', 'CREA — Consiglio per la ricerca in agricoltura', 'RESEARCH_INSTITUTION', 'INSTAGRAM',
      'declarado em crea.gov.it (leitura 2026-09-03)',
      'centro nacional de pesquisa agricola; ja e fonte do acervo pelo site, nunca pelo canal',
      ['TODAS'], 2),
    C('arpaeemiliaromagna', 'Arpae Emilia-Romagna', 'PUBLIC_BODY', 'INSTAGRAM',
      'declarado em arpae.it (leitura 2026-09-03)',
      'agrometeorologia da regiao onde estao 4 das 37 oportunidades e toda a serie da cimice',
      ['TODAS'], 2),
    C('unicatt', 'Universita Cattolica del Sacro Cuore', 'UNIVERSITY', 'INSTAGRAM',
      'declarado em piacenza.unicatt.it (leitura 2026-09-03)',
      'casa dos modelos CERCOPRI/CERCODEP de cercospora da barbabietola, a cultura de maior '
      'peso de rotulo ADAMA (239 pares)',
      ['BARBABIETOLA', 'VITE', 'FRUMENTO'], 2),
    C('distal.unibo', 'UNIBO — DISTAL', 'UNIVERSITY_DEPARTMENT', 'INSTAGRAM',
      'declarado em distal.unibo.it (leitura 2026-09-03)',
      'departamento agro-alimentar de Bolonha; a mesma universidade opera a rede de trappole '
      'da cimice em big.csr.unibo.it',
      ['MELO', 'PERO', 'BARBABIETOLA', 'POMODORO'], 2),
    C('dafnaeunipd', 'UNIPD — DAFNAE', 'UNIVERSITY_DEPARTMENT', 'INSTAGRAM',
      'declarado em dafnae.unipd.it (leitura 2026-09-03)',
      'departamento de agronomia de Padova, no Veneto — regiao de OPP_75C37DED9160 e '
      'OPP_EA2AE1EFB775',
      ['VITE', 'MAIS', 'SOIA', 'POMODORO'], 2),
    C('disaa_unimi', 'UNIMI — DiSAA', 'UNIVERSITY_DEPARTMENT', 'INSTAGRAM',
      'declarado em disaa.unimi.it (leitura 2026-09-03)',
      'agronomia de Milao, Lombardia — regiao de OPP_F6EEF5B32F65 (mais x diabrotica)',
      ['MAIS', 'RISO', 'VITE'], 2),

    # ── PRIORIDADE 3 · voz de produtor agregada e midia tecnica ──
    C('cia_agricoltori', 'CIA — Agricoltori Italiani', 'PRODUCER_ORGANISATION', 'INSTAGRAM',
      'declarado em cia.it (leitura 2026-09-03)', 'organizacao nacional de produtores',
      ['TODAS'], 3),
    C('coldiretti', 'Coldiretti', 'PRODUCER_ORGANISATION', 'INSTAGRAM',
      'declarado em coldiretti.it (leitura 2026-09-03)',
      'ja e fonte do acervo pelo site; o canal nao estava', ['TODAS'], 3),
    C('confagricolturasiena', 'Unione Provinciale Agricoltori di Siena', 'PRODUCER_ORGANISATION', 'INSTAGRAM',
      'declarado em confagricolturasiena.it (leitura 2026-09-03)',
      'republica o bollettino fitossanitario da Toscana — regiao de OPP_IT-WIN-0029 (grano duro '
      'x fusariose, proxima janela 2027)',
      ['VITE', 'OLIVO', 'FRUMENTO'], 3),
    C('agronotizie', 'AgroNotizie (Image Line s.r.l.)', 'TECHNICAL_MEDIA', 'INSTAGRAM',
      'declarado no RSS de agronotizie.imagelinenetwork.com (leitura 2026-09-03)',
      'principal midia tecnica agricola italiana. ATENCAO: a editora e Image Line s.r.l. em '
      'imagelinenetwork.com — image-line.com e a FL Studio, outra empresa',
      ['TODAS'], 3),
    C('edagricole_official', 'Edagricole / Tecniche Nuove', 'TECHNICAL_MEDIA', 'INSTAGRAM',
      'declarado em edagricole.it, terraevita, VVQ, Olivo e Olio, Rivista Orticoltura (leitura 2026-09-03)',
      'grupo editorial que publica as revistas de cultura unica das culturas ADAMA',
      ['VITE', 'OLIVO', 'ORTAGGI'], 3),
    C('masafsocial', 'MASAF — Ministero dell agricoltura', 'PUBLIC_BODY', 'INSTAGRAM',
      'declarado em politicheagricole.it (leitura 2026-09-03)',
      'ministerio; camada de politica e de evento regulatorio', ['TODAS'], 3),
    C('coneglianovaldobbiadenedocg', 'Consorzio Conegliano Valdobbiadene Prosecco DOCG',
      'CONSORTIUM', 'INSTAGRAM',
      'declarado em prosecco.it (leitura 2026-09-03)',
      'consorcio de tutela no Veneto — vite, a cultura de OPP_AF16E6A6B8B3 e OPP_68984FFD5ABF '
      '(flavescenza dorata)',
      ['VITE'], 3),

    # ── LINKEDIN · a camada que na Espanha foi a unica a resolver pais e papel ──
    C('company/apofruit-italia-soc-coop-agricola', 'Apofruit Italia', 'COOPERATIVE', 'LINKEDIN',
      'declarado em apofruit.it (leitura 2026-09-03)',
      'OP de fruta; LinkedIn e onde papel declarado e pais declarado existem como campo',
      ['MELO', 'PERO', 'PESCO', 'FRAGOLA'], 2),
    C('company/arpae-emilia-romagna', 'Arpae Emilia-Romagna', 'PUBLIC_BODY', 'LINKEDIN',
      'declarado em arpae.it (leitura 2026-09-03)', 'agrometeorologia regional', ['TODAS'], 3),
    C('company/vog-apples', 'VOG — Consorzio delle mele dell Alto Adige', 'PRODUCER_ORGANISATION', 'LINKEDIN',
      'declarado em vog.it (leitura 2026-09-03)',
      'maior consorcio de maca da Italia; MELO tem 146 pares de rotulo ADAMA', ['MELO'], 2),
    C('company/nufarm', 'Nufarm', 'COMPANY', 'LINKEDIN',
      'declarado em nufarm.com/it (leitura 2026-09-03)',
      'concorrente no bloco de erbicidi, onde a ADAMA Italia tem 26 dos 51 produtos comerciais',
      ['FRUMENTO', 'MAIS', 'VITE'], 2),
    C('company/cia-agricoltori-italiani', 'CIA — Agricoltori Italiani', 'PRODUCER_ORGANISATION', 'LINKEDIN',
      'declarado em cia.it (leitura 2026-09-03)', 'organizacao nacional de produtores', ['TODAS'], 3),

    # ── YOUTUBE · a camada de video que a REGRA DE COLETA EXTERNA poe em 1o lugar ──
    C('@agraliastudio', 'Agralia Studio Agronomico', 'TECHNICAL_ADVISORY', 'YOUTUBE',
      'declarado em agralia.it (leitura 2026-09-03)', 'voz tecnica privada de vite na Lombardia',
      ['VITE', 'OLIVO'], 1),
    C('channel/UCktJyIUm3qJJpThrTa8nsHQ', 'AIPP', 'SCIENTIFIC_SOCIETY', 'YOUTUBE',
      'declarado em aipp.it (leitura 2026-09-03)', 'protecao das plantas, fala tecnica longa',
      ['TODAS'], 1),
    C('channel/UCWjrNnyRiWOtCM0zKUcsK5A', 'FMC Agro Italia', 'COMPANY', 'YOUTUBE',
      'declarado em ag.fmc.com/it (leitura 2026-09-03)', 'comunicacao tecnica de concorrente em italiano',
      ['VITE', 'MAIS', 'POMODORO'], 1),
    C('user/GowanItalia', 'Gowan Italia', 'COMPANY', 'YOUTUBE',
      'declarado em gowanitalia.it (leitura 2026-09-03)', 'concorrente ausente do acervo, difesa della vite',
      ['VITE', 'POMODORO', 'MELO'], 2),
    C('@SIRFI-k9x', 'SIRFI — Societa Italiana per la Ricerca sulla Flora Infestante',
      'SCIENTIFIC_SOCIETY', 'YOUTUBE',
      'declarado em sirfi.it (leitura 2026-09-03)',
      'a sociedade italiana de plantas infestantes — erbicidi sao 26 dos 51 produtos ADAMA Italia',
      ['FRUMENTO', 'MAIS', 'RISO', 'SOIA', 'BARBABIETOLA'], 1),
    C('channel/UCoA303PgO9oOBWgZ3Nl5GvQ', 'Agrintesa', 'COOPERATIVE', 'YOUTUBE',
      'declarado em agrintesa.it (leitura 2026-09-03)', 'cooperativa das pomacee da Romagna',
      ['MELO', 'PERO', 'ACTINIDIA'], 2),
    C('@myfruitvideo', 'Myfruit', 'TECHNICAL_MEDIA', 'YOUTUBE',
      'declarado em myfruit.it (leitura 2026-09-03)', 'video de ortofrutta italiana',
      ['MELO', 'PERO', 'PESCO'], 3),
    C('user/TerremerseCoop', 'Terremerse', 'COOPERATIVE_DISTRIBUTOR', 'YOUTUBE',
      'declarado em terremerse.it (leitura 2026-09-03)',
      'cooperativa que tambem distribui agrofarmaco nas culturas de maior peso de rotulo',
      ['FRUMENTO', 'MAIS', 'BARBABIETOLA', 'POMODORO'], 2),
]


def escrever():
    os.makedirs(SAIDA, exist_ok=True)
    from collections import Counter
    corpo = {
        'SOURCE_ID': 'PUBLIC-COMM-IT-SOCIAL-BATCH-V1',
        'DATASET_OWNER': 'SINTONIA_SCRAP_ITALY',
        'VERSION': 'V1',
        'FROZEN_AT': CAPTURA,
        'CAPTURED_AT': CAPTURA,
        'CAPTURED_AT_POR_QUE': ('DERIVED_SCOPE: a lista nao foi capturada do mundo, foi derivada de '
                                'leituras de site feitas nesta missao. A data em que passou a existir '
                                'E a data do congelamento.'),
        'FROZEN_RULE': ('esta lista NAO muda depois da primeira coleta. Criterio novo produz V2 '
                        'explicita, com a V1 preservada — senao o rendimento fica medido contra um '
                        'denominador que se mexeu.'),
        'ENTRY_RULE': 'ACCOUNT_IDENTITY_STATE = DECLARED_BY_THE_ORGANISATION',
        'WHY_THE_RULE_IS_THIS_NARROW': ('ES-T8-003 reprovou com 39 de 60 itens agronomicos porque 24 de '
                                        '32 contas nao declaravam pais. Volume nao compensa identidade ausente.'),
        'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'APIFY_RUNS': 0,
        'COST_USD': 0,
        'ACCOUNTS_IN_BATCH': len(CONTAS),
        'BY_PLATFORM': dict(Counter(c['PLATFORM'] for c in CONTAS)),
        'BY_PAGE_ROLE': dict(Counter(c['PAGE_ROLE'] for c in CONTAS)),
        'BY_PRIORITY': dict(Counter(c['COLLECTION_PRIORITY'] for c in CONTAS)),
        'EXECUTION_ORDER': [
            {'STEP': 'A', 'FASE': 'janela-perfis', 'CUSTO': 'ZERO',
             'GATE': 'rota publica pelo navegador — bio, seguidores e o denominador de posts'},
            {'STEP': 'B', 'FASE': 'janela-objetos', 'CUSTO': 'ZERO',
             'GATE': 'os 12 itens recentes, legenda inteira, data, curtidas e — em reel — duracao e MP4'},
            {'STEP': 'C', 'FASE': 'transcrever', 'CUSTO': 'ZERO em dolar, tempo de maquina',
             'GATE': 'faster-whisper small, idioma it DECLARADO, nunca detectado'},
            {'STEP': 'D', 'FASE': 'comentarios', 'CUSTO': 'PAGA',
             'GATE': 'so atras do portao de dado pessoal, e so se as tres fases gratis fecharem sem PARTIAL'},
        ],
        'WINDOW_FIRST': 'LAST_30D',
        'WINDOW_WIDEN_TO': 'LAST_60D, depois LAST_90D',
        'WINDOW_WIDEN_RULE': 'so onde o corpus vier baixo. Nunca historico profundo na primeira execucao.',
        'CONTENT_COLLECTION_STAGE': 'NOT_STARTED',
        'MISSION_STATE': 'READY_TO_COLLECT_WHEN_RUNNER_AVAILABLE',
        'WHY_NOT_COLLECTED_HERE': ('esta sessao remota nao tem a rota: o Chrome nao atravessa o proxy '
                                   '(ERR_CONNECTION_RESET em todo host, google.com incluido) e a pagina '
                                   'de perfil do Instagram devolve HTTP 302 para login. A rota de EMBED '
                                   'de POST responde HTTP 200 daqui — falta o shortcode, que a passada '
                                   'de perfil entrega. O `sintonia-scrap.yml` roda no self-hosted que tem '
                                   'navegador e nucleos.'),
        'ZERO_MEANS_NOW': 'NO_CONTENT_COLLECTION_EXECUTED — nenhum zero deste lote fala sobre o mundo ainda',
        'ZERO_WILL_MEAN_AFTER_A_VALID_RUN': ('NO_ITEMS_OBSERVED nesta conta provada, nesta plataforma, '
                                             'nesta janela, nesta execucao bem-sucedida. NUNCA '
                                             'ORGANIZATION_NOT_COMMUNICATING.'),
        'ACCOUNTS': CONTAS,
    }
    caminho = os.path.join(SAIDA, 'PUBLIC-COMM-IT-SOCIAL-BATCH-V1.json')
    with open(caminho, 'w', encoding='utf-8') as fh:
        json.dump(corpo, fh, ensure_ascii=False, indent=1)
    return caminho, corpo


if __name__ == '__main__':
    caminho, corpo = escrever()
    print('escrito: %s' % os.path.relpath(caminho, ROOT))
    print()
    for k in ('ACCOUNTS_IN_BATCH', 'BY_PLATFORM', 'BY_PAGE_ROLE', 'BY_PRIORITY', 'MISSION_STATE'):
        print('%-22s %s' % (k, corpo[k]))
