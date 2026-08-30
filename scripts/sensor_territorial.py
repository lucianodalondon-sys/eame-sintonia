#!/usr/bin/env python3
"""
COLETA TERRITORIAL — itens das fontes vivas, com localidade medida e não presumida.

    python3 scripts/sensor_territorial.py coletar [A|B]
    python3 scripts/sensor_territorial.py medir

A REGRA DE HERANÇA TERRITORIAL, QUE É O CORAÇÃO DESTE TESTE
-------------------------------------------------------------
A arbitragem levantou a hipótese de que fonte com mandato territorial carrega localidade
naturalmente. Ela mandou TESTAR, não assumir — e a diferença entre as duas coisas é esta
função, `lugar_do_fato()`, que herda em uns casos e recusa em outros.

    HERDA quando a fonte é um serviço fitossanitário / extensão / estação experimental
    COM mandato sobre uma REGIÃO específica, E o item é um BOLETIM dela. Um boletim
    fitossanitário do Veneto sobre a videira do Veneto tem lugar do fato: é a própria
    razão de ele existir.

    NÃO HERDA de imprensa técnica, nem de organização nacional, nem de notícia solta.
    A Arvalis é francesa e cobre a França inteira: um artigo dela não localiza fato.
    A universidade sediada numa região não faz da região o local do experimento.

    E NUNCA herda de idioma. O piloto anterior mediu isso: consulta em espanhol devolveu
    vídeo italiano e vídeo uruguaio.

        MANDATO TERRITORIAL != LUGAR DO FATO. IDIOMA != LUGAR.

Quando não herda e o texto não nomeia lugar, sai `NOT_KNOWN`. É a resposta certa, e é a
razão de a rota anterior ter reprovado honestamente em 26% em vez de fabricar 100%.

O QUE ESTE ARQUIVO NÃO FAZ
---------------------------
Não declara Early Signal, não mede antecedência, não cria score. Ele produz a unidade de
observação com proveniência e entrega para a arbitragem.
"""
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fonte_territorial as ft  # noqa: E402

SAIDA = os.path.join(ROOT, 'data', 'samples', 'TERRITORIAL')
NAO_SEI = 'NOT_KNOWN'
MISSION = '16-ROTA-TERRITORIAL'
OWNER = 'EARLY_SIGNAL_EAME'

LOTES = {
    'A': ['ES-OLIVE-REPILO', 'IT-DURUM_WHEAT-FUSARIUM', 'FR-VINE-DOWNY_MILDEW'],
    'B': ['ES-CEREAL-SEPTORIA', 'IT-VINE-FLAVESCENCE', 'FR-CEREAL-SEPTORIA'],
}

# Tipos de fonte cujo mandato PODE ser herdado como lugar do fato — quando o item é um
# boletim dela. Imprensa técnica está deliberadamente fora.
TIPOS_QUE_HERDAM = ('REGIONAL_PHYTOSANITARY_SERVICE', 'EXTENSION_SERVICE',
                    'EXPERIMENTAL_STATION')

# Mandato NACIONAL não localiza. Só região localiza.
MANDATO_NACIONAL = ('España', 'Italia', 'France')

MARCA_BOLETIM = ('bollettin', 'boletin', 'boletín', 'bulletin', 'aviso', 'avvis',
                 'butlleti', 'butlletí', 'bsv')

# ── vocabulário de conteúdo, multilíngue e declarado ─────────────────────────────
CROPS = {
    'OLIVE': ('olivo', 'olivar', 'olive', 'olivier', 'oliveto', 'aceituna'),
    'CEREAL': ('trigo', 'cereal', 'blé', 'ble', 'frumento', 'grano', 'cereali',
               'cebada', 'orzo', 'triticum'),
    'DURUM_WHEAT': ('grano duro', 'trigo duro', 'blé dur', 'frumento duro', 'durum'),
    'VINE': ('vid', 'viña', 'vinya', 'vite', 'vigneto', 'vigne', 'vignoble',
             'grapevine', 'uva', 'raïm'),
}
ISSUES = {
    'REPILO': ('repilo', 'venturia oleaginea', 'spilocaea'),
    'SEPTORIA': ('septoria', 'zymoseptoria', 'septoriosi', 'septoriose', 'septoriosis'),
    'FUSARIUM': ('fusari', 'micotossin', 'micotoxin', 'mycotoxin', 'don ', 'deossiniv'),
    'FLAVESCENCE': ('flavescen', 'giallumi', 'phytoplasma', 'fitoplasma'),
    'DOWNY_MILDEW': ('mildiu', 'mildiou', 'plasmopara', 'peronospora'),
}

OBSERVACAO = [
    ('FIELD_OBSERVATION', ('si osserva', 'si segnala', 'rilevat', 'osservat',
                           'se observa', 'se detecta', 'detectad', 'observad',
                           'on observe', 'constaté', 'relevé', 'presencia de',
                           'presenza di', 'primeros síntomas', 'primi sintomi')),
    ('PHENOLOGY_UPDATE', ('fase fenologic', 'estado fenológico', 'stade phénologique',
                          'bbch', 'floración', 'fioritura', 'floraison', 'spigatura',
                          'espigado', 'épiaison')),
    ('TECHNICAL_ALERT', ('alerta', 'allerta', 'alerte', 'atención', 'attenzione',
                         'attention', 'avviso urgente')),
    ('RISK_WARNING', ('rischio', 'riesgo', 'risque', 'condizioni favorevoli',
                      'condiciones favorables', 'conditions favorables',
                      'previsione', 'previsión', 'prévision')),
    ('TREATMENT_GUIDANCE', ('trattament', 'tratamiento', 'traitement', 'intervenir',
                            'intervento', 'intervención', 'aplicar', 'applicare',
                            'appliquer', 'se recomienda', 'si consiglia',
                            'il est conseillé')),
    ('REGULATORY_UPDATE', ('autorizzazion', 'autorización', 'autorisation',
                           'revoca', 'revocación', 'retrait', 'registro', 'ephy')),
    ('RESEARCH_COMMUNICATION', ('estudio', 'studio', 'étude', 'ensayo', 'prova',
                                'essai', 'investigación', 'ricerca', 'recherche')),
]

# Regiões nomeadas, por país. Lista fechada e auditável — não é dicionário de geografia.
REGIOES = {
    'ES': ('andalucía', 'andalucia', 'córdoba', 'cordoba', 'jaén', 'jaen', 'sevilla',
           'granada', 'huelva', 'cádiz', 'cadiz', 'málaga', 'almería', 'aragón',
           'aragon', 'huesca', 'zaragoza', 'teruel', 'catalunya', 'cataluña',
           'lleida', 'girona', 'tarragona', 'extremadura', 'badajoz', 'cáceres',
           'castilla y león', 'castilla-la mancha', 'navarra', 'la rioja'),
    'IT': ('veneto', 'lombardia', 'piemonte', 'emilia-romagna', 'emilia romagna',
           'toscana', 'umbria', 'puglia', 'friuli', 'trentino',
           'alto adige', 'sicilia', 'sardegna', 'campania', 'abruzzo', 'molise',
           'basilicata', 'calabria', 'liguria', 'lazio', 'foggia', 'verona',
           # 'marche' NAO entra sozinha: em italiano e palavra comum
           # (marcas), e ja produziu pais errado uma vez nesta missao.
           'regione marche', 'le marche',
           'treviso', 'conegliano', 'valpolicella'),
    'FR': ('nouvelle-aquitaine', 'occitanie', 'grand est', 'bourgogne', 'champagne',
           'alsace', 'beaujolais', 'gironde', 'bordeaux', 'charente', 'bretagne',
           'normandie', 'hauts-de-france', 'centre-val de loire', 'beauce',
           'languedoc', 'provence', 'val de loire'),
}


def _n(s):
    return re.sub(r'\s+', ' ', str(s or '')).lower()


def _tem(texto, termos):
    for t in termos:
        if t in texto:
            return t
    return None


def _buscar(url, timeout=35):
    req = urllib.request.Request(url, headers={
        'User-Agent': ft.UA, 'Accept': 'text/html,*/*',
        'Accept-Language': 'es,it,fr,en;q=0.8'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(2000000).decode('utf-8', 'replace'), None
    except urllib.error.HTTPError as e:
        return e.code, '', 'HTTP %d' % e.code
    except Exception as e:                                    # noqa: BLE001
        try:
            r = subprocess.run(['curl', '-sSL', '--max-time', str(timeout),
                                '-A', ft.UA, url], capture_output=True,
                               timeout=timeout + 10)
            if r.returncode == 0 and r.stdout:
                return 200, r.stdout.decode('utf-8', 'replace'), None
        except Exception:                                     # noqa: BLE001
            pass
        return None, '', type(e).__name__


LINK = re.compile(r'<a\s[^>]*href="([^"#]+)"[^>]*>(.{0,220}?)</a>', re.I | re.S)


def _itens_da_pagina(texto, base, hoje):
    """Extrai (url, título, data) da listagem. Data só quando o TEXTO a nomeia."""
    raiz = re.match(r'(https?://[^/]+)', base)
    raiz = raiz.group(1) if raiz else base
    fora, vistos = [], set()
    for m in LINK.finditer(texto):
        href = m.group(1)
        titulo = ' '.join(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
        if not titulo or len(titulo) < 12:
            continue
        if href.startswith('/'):
            href = raiz + href
        if not href.startswith('http'):
            continue
        if href in vistos:
            continue
        # A data pode estar no rótulo do link OU no próprio caminho da URL.
        datas = ft.datas_no_texto(titulo) or ft.datas_no_texto(href)
        if not datas:
            m2 = re.search(r'/(20\d{2})/(\d{1,2})/(\d{1,2})/', href)
            if m2:
                try:
                    datas = [datetime.date(int(m2.group(1)), int(m2.group(2)),
                                           int(m2.group(3)))]
                except ValueError:
                    datas = []
        vistos.add(href)
        fora.append({'URL': href, 'TITLE': titulo[:240],
                     'DATE': datas[-1].isoformat() if datas else NAO_SEI})
    return fora


def lugar_do_fato(fonte, titulo, texto):
    """A REGRA. Devolve (country, region, base, evidência).

    Ordem: lugar NOMEADO no texto vence sempre. Só na ausência dele a herança de mandato
    é considerada — e só para fonte regional com item que é boletim dela.
    """
    corpo = _n('%s %s' % (titulo, texto[:LEAD_CHARS]))
    pais = fonte['SOURCE_COUNTRY']
    # 1. LUGAR NOMEADO. É a evidência mais forte e não depende de nenhuma suposição.
    achou = _tem(corpo, REGIOES.get(pais, ()))
    if achou:
        return pais, achou, 'NAMED_IN_TEXT', 'o texto nomeia "%s"' % achou
    # 2. HERANÇA DE MANDATO, restrita.
    regional = (fonte['SOURCE_TYPE'] in TIPOS_QUE_HERDAM
                and fonte['MANDATE_GEOGRAPHY'] not in MANDATO_NACIONAL)
    e_boletim = bool(_tem(_n(titulo), MARCA_BOLETIM))
    if regional and e_boletim:
        return (pais, fonte['MANDATE_GEOGRAPHY'], 'INHERITED_FROM_MANDATE',
                'boletim de %s, cujo mandato declarado é %s — o item existe para '
                'relatar aquele território' % (fonte['SOURCE_NAME'][:40],
                                               fonte['MANDATE_GEOGRAPHY']))
    # 3. NADA. E isso é resposta, não falha.
    motivo = ('imprensa/organização nacional não localiza fato'
              if not regional else 'o item não se anuncia como boletim da fonte')
    return NAO_SEI, NAO_SEI, 'NOT_INHERITED', motivo


def classificar(titulo, texto):
    corpo = _n('%s %s' % (titulo, texto))
    for tipo, termos in OBSERVACAO:
        achou = _tem(corpo, termos)
        if achou:
            return tipo, 'termo "%s"' % achou
    return 'OTHER', 'nenhum marcador dos léxicos declarados'


JANELA_TEMA = 600
# So o COMECO do documento conta como o documento. Barra lateral vem depois.
LEAD_CHARS = 3000


def _perto(corpo, termos_a, termos_b, janela=JANELA_TEMA):
    """`a` que tenha algum `b` a menos de `janela` caracteres."""
    for t in termos_a:
        i = corpo.find(t)
        while i != -1:
            trecho = corpo[max(0, i - janela): i + len(t) + janela]
            if _tem(trecho, termos_b):
                return t
            i = corpo.find(t, i + 1)
    return None


def crop_issue(titulo, texto):
    """Cultura e problema, com PROXIMIDADE entre os dois.

    A primeira versao casava contra o texto inteiro da pagina. Num site de noticias a
    pagina traz a barra lateral com chamadas para todos os outros artigos — entao TODO
    artigo saiu com OLIVE+DURUM_WHEAT+VINE e FUSARIUM+FLAVESCENCE+DOWNY_MILDEW, inclusive
    um sobre "diserbo delle brassicacee".

        CO-OCORRENCIA NA PAGINA NAO E ASSUNTO DO ARTIGO.

    E o mesmo defeito de janela larga que a matriz de recorte ja tinha pago. O titulo
    continua valendo sozinho, porque titulo E o artigo; o corpo so vale com vizinhanca.
    """
    # A JANELA DE LEITURA. Exigir cultura E problema juntos derrubou os seis boletins
    # reais de Extremadura — que nomeiam a cultura e nao nomeiam doenca no resumo — e
    # manteve os artigos de portal com barra lateral. O filtro certo tem de valer para o
    # boletim curto E para a noticia longa.
    #
    # A vizinhanca deixa de ser entre cultura e problema, e passa a ser a POSICAO no
    # documento: o comeco de um artigo e o artigo; o fim da pagina e a barra lateral com
    # chamadas para tudo o mais que o site publica.
    #
    #     PAGINA != ARTIGO. E foi a pagina inteira que fez "diserbo delle brassicacee"
    #     sair como olivar com flavescencia.
    tit = _n(titulo)
    corpo = _n(texto)[:LEAD_CHARS]
    crops = [c for c, ts in CROPS.items() if _tem(tit, ts) or _tem(corpo, ts)]
    issues = [i for i, ts in ISSUES.items() if _tem(tit, ts) or _tem(corpo, ts)]
    # DURUM_WHEAT implica CEREAL, e o específico manda.
    if 'DURUM_WHEAT' in crops and 'CEREAL' in crops:
        crops.remove('CEREAL')
    return crops, issues


def coletar(lote='A'):
    with open(os.path.join(SAIDA, 'INVENTARIO-DE-FONTES.json'), encoding='utf-8') as f:
        inv = json.load(f)
    hoje = datetime.date.today()
    casos = LOTES[lote]
    # Só fonte ALCANÇADA e que serve algum recorte deste lote. Fonte morta não entra, e
    # o motivo dela continua no inventário — nunca some.
    fontes = [s for s in inv['SOURCES']
              if s['REACHABLE'] and set(s['SERVES_CASES']) & set(casos)]
    print('lote %s · %d fontes vivas para %s' % (lote, len(fontes), casos))
    itens, por_fonte = [], {}
    for fo in fontes:
        status, html, motivo = _buscar(fo['URL_FETCHED'])
        if status != 200:
            print('  %-18s INDISPONIVEL agora (%s)' % (fo['SOURCE_ENTITY_ID'], motivo))
            por_fonte[fo['SOURCE_ENTITY_ID']] = 0
            continue
        brutos = _itens_da_pagina(html, fo['URL_FETCHED'], hoje)
        n = 0
        for b in brutos:
            crops, issues = crop_issue(b['TITLE'], '')
            # O item precisa tocar o recorte. Sem cultura NEM problema, é item da casa,
            # não do experimento — e contá-lo inflaria o denominador com ruído.
            if not crops and not issues:
                continue
            pais, regiao, base, ev = lugar_do_fato(fo, b['TITLE'], '')
            tipo, tev = classificar(b['TITLE'], '')
            casos_do_item = [c for c in casos
                             if c.split('-')[0] == fo['SOURCE_COUNTRY']
                             and (c.split('-', 1)[1].rsplit('-', 1)[0] in crops
                                  or c.rsplit('-', 1)[1] in issues)]
            itens.append({
                'ITEM_ID': '%s::%s' % (fo['SOURCE_ENTITY_ID'],
                                       re.sub(r'\W+', '-', b['URL'])[-60:]),
                'DATASET_OWNER': OWNER, 'MISSION_ID': MISSION,
                'BATCH_ID': 'TERRITORIAL-%s' % lote,
                'SOURCE_ENTITY_ID': fo['SOURCE_ENTITY_ID'],
                'SOURCE_NAME': fo['SOURCE_NAME'], 'SOURCE_TYPE': fo['SOURCE_TYPE'],
                'SOURCE_URL': b['URL'],
                'SOURCE_COUNTRY': fo['SOURCE_COUNTRY'],
                'SOURCE_REGION': fo['SOURCE_REGION'],
                'MANDATE_GEOGRAPHY': fo['MANDATE_GEOGRAPHY'],
                'PUBLISHED_AT': b['DATE'],
                'CAPTURED_AT': hoje.isoformat(),
                'COUNTRY_OF_FACT': pais, 'REGION_OF_FACT': regiao,
                'LOCALITY_BASIS': base, 'LOCALITY_EVIDENCE': ev,
                'CROP': crops or NAO_SEI, 'ISSUE': issues or NAO_SEI,
                'CASES': casos_do_item or NAO_SEI,
                'OBSERVATION_TYPE': tipo, 'OBSERVATION_TYPE_EVIDENCE': tev,
                'OBSERVATION_TEXT': b['TITLE'],
                # Originalidade não é presumida: sem ler o corpo do documento, o máximo
                # honesto é NOT_KNOWN. Título não prova autoria de observação.
                'ORIGINAL_OBSERVATION': NAO_SEI,
                'ORIGINAL_OBSERVATION_OWNER': (fo['SOURCE_NAME']
                                               if fo['SOURCE_TYPE'] in TIPOS_QUE_HERDAM
                                               else NAO_SEI),
                'EVIDENCE_OF_ORIGINALITY': ('só o título foi lido nesta passagem; '
                                            'autoria de observação exige o corpo'),
                'PROVENANCE': {'ROUTE': fo['ACCESS_ROUTE'], 'TOOL': 'HTTP_DIRECT',
                               'APIFY': False, 'LISTING_URL': fo['URL_FETCHED']},
            })
            n += 1
        por_fonte[fo['SOURCE_ENTITY_ID']] = n
        print('  %-18s %-28s %3d itens do recorte' % (
            fo['SOURCE_ENTITY_ID'], fo['SOURCE_TYPE'][:28], n))
    corpo = {
        'SOURCE_ID': 'TERRITORIAL/ITENS-%s' % lote,
        'DATASET_OWNER': OWNER, 'MISSION_ID': MISSION,
        'source': 'coleta HTTP direta das listagens públicas — zero Apify',
        'SOURCE_LOCATION': 'ES, IT, FR',
        'FACT_LOCATION': 'ver COUNTRY_OF_FACT por item',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': hoje.isoformat(), 'CAPTURED_AT': hoje.isoformat(),
        'LOTE': lote, 'CASES': casos,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'SOURCES_QUERIED': len(fontes), 'ITEMS_BY_SOURCE': por_fonte,
        'ITEMS_COUNT': len(itens),
        'LIMITE_DECLARADO': ('esta passagem lê a LISTAGEM, não o corpo de cada boletim. '
                             'CROP, ISSUE e tipo de observação saem do título. '
                             'Originalidade fica NOT_KNOWN por isso.'),
        'ITEMS': itens,
    }
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'ITENS-%s.json' % lote), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\n%d itens · gravado em data/samples/TERRITORIAL/ITENS-%s.json'
          % (len(itens), lote))
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'coletar'
    lote = (sys.argv[2] if len(sys.argv) > 2 else 'A').upper()
    raise SystemExit(coletar(lote))
