#!/usr/bin/env python3
"""
INVENTÁRIO DE FONTES TERRITORIAIS — fonte primeiro, ferramenta depois.

    python3 scripts/fonte_territorial.py sondar     # mede cada fonte, sem coletar
    python3 scripts/fonte_territorial.py resumo

A HIPÓTESE QUE ESTE ARQUIVO EXISTE PARA TESTAR
-----------------------------------------------
A rota pessoal/social reprovou no indicador bloqueador: `COUNTRY_OF_FACT` em 26% contra
piso de 50%, e 16 vídeos em 180 dias entre 440. A arbitragem levantou a hipótese de que
fontes com **mandato territorial** — serviço fitossanitário regional, boletim técnico,
imprensa técnica local — carregam país, região, cultura, problema e data como propriedades
NATURAIS, e não como inferência posterior.

    ISSO É HIPÓTESE. ESTE ARQUIVO MEDE, NÃO ASSUME.

Uma fonte só entra no experimento depois de responder, medido: ela existe, ela abre, ela
publica, e ela publicou RECENTEMENTE. Fonte com arquivo rico e silêncio de dois anos é
arquivo, não sensor — e o piloto anterior já mostrou como é fácil confundir os dois.

MANDATO TERRITORIAL NÃO É LUGAR DO FATO
-----------------------------------------
`MANDATE_GEOGRAPHY` é o território sobre o qual a fonte tem competência declarada.
`REGION_OF_FACT` é onde o fato observado aconteceu. Eles COINCIDEM em um boletim
fitossanitário regional que relata a situação daquela região — e NÃO coincidem num artigo
genérico de uma universidade sediada ali.

A herança territorial é uma REGRA EXECUTÁVEL (ver `sensor_territorial.py`), nunca um
atalho. É a mesma distinção que já custou caro aqui: `SOURCE_LOCATION != FACT_LOCATION`.

POR QUE NENHUMA FERRAMENTA APARECE NESTE ARQUIVO
--------------------------------------------------
Ele mede `CONTENT_FORMAT` e `ACCESS_ROUTE` e para. Escolher Apify antes de saber se a
fonte é um PDF estático seria escolher ferramenta antes de conhecer o problema — e o
contrato é explícito: a melhor ferramenta é a que preserva a evidência mais corretamente,
não a que já está paga.
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
SAIDA = os.path.join(ROOT, 'data', 'samples', 'TERRITORIAL')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

NAO_SEI = 'NOT_KNOWN'

# ── CANDIDATAS, DECLARADAS ───────────────────────────────────────────────────────
# Cada linha é uma aposta explícita e auditável, com o recorte que ela serve. Nenhuma foi
# descoberta por hashtag ou busca aberta: são os órgãos e institutos que têm mandato
# declarado sobre aquele território e aquela cultura.
#
# As italianas vêm do mapa que o piloto italiano já preservou (IT-SENSORES-V2), com URL e
# data de última publicação medidas. Reaproveitar é a decisão certa — redescobrir custaria
# tempo e devolveria a mesma lista.
#
# (chave, nome, tipo, país, região/mandato, url, recortes que serve)
FONTES = [
    # ── ES ───────────────────────────────────────────────────────────────────────
    ('ES-RAIF', 'RAIF — Red de Alerta e Información Fitosanitaria de Andalucía',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'ES', 'Andalucía',
     'https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif',
     ['ES-OLIVE-REPILO', 'ES-CEREAL-SEPTORIA']),
    ('ES-ARAGON-AVISOS', 'Centro de Sanidad y Certificación Vegetal de Aragón',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'ES', 'Aragón',
     'https://www.aragon.es/-/boletines-fitosanitarios',
     ['ES-CEREAL-SEPTORIA']),
    ('ES-CAT-AVISOS', 'Servei de Sanitat Vegetal — Generalitat de Catalunya',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'ES', 'Catalunya',
     'https://agricultura.gencat.cat/ca/ambits/agricultura/'
     'dar_sanitat_vegetal_nou/avisos-fitosanitaris/',
     ['ES-CEREAL-SEPTORIA']),
    ('ES-JUNTAEX', 'Servicio de Sanidad Vegetal — Junta de Extremadura',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'ES', 'Extremadura',
     'https://www.juntaex.es/temas/agricultura-ganaderia/sanidad-vegetal',
     ['ES-OLIVE-REPILO', 'ES-CEREAL-SEPTORIA']),
    ('ES-JCYL-BOLETIN', 'Boletín Fitosanitario de Avisos — Junta de Castilla y León',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'ES', 'Castilla y León',
     'https://agriculturaganaderia.jcyl.es/web/es/sanidad-vegetal/'
     'boletines-fitosanitarios-avisos.html',
     ['ES-CEREAL-SEPTORIA']),
    ('ES-IFAPA', 'IFAPA — Instituto de Investigación y Formación Agraria y Pesquera',
     'EXTENSION_SERVICE', 'ES', 'Andalucía',
     'https://www.juntadeandalucia.es/agriculturaypesca/ifapa/',
     ['ES-OLIVE-REPILO', 'ES-CEREAL-SEPTORIA']),
    ('ES-OLIMERCA', 'Olimerca — imprensa técnica do olivar',
     'TECHNICAL_PRESS', 'ES', 'España', 'https://www.olimerca.com/',
     ['ES-OLIVE-REPILO']),
    ('ES-AGRONEGOCIOS', 'Agronegocios — imprensa técnica agrícola',
     'TECHNICAL_PRESS', 'ES', 'España', 'https://www.agronegocios.es/',
     ['ES-OLIVE-REPILO', 'ES-CEREAL-SEPTORIA']),

    # ── IT ───────────────────────────────────────────────────────────────────────
    ('IT-ERSA-FVG', 'ERSA FVG — Servizio fitosanitario e chimico',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'IT', 'Friuli-Venezia Giulia',
     'https://www.ersa.fvg.it/aziende/difesa-delle-colture/bollettini-fitosanitari/',
     ['IT-DURUM_WHEAT-FUSARIUM', 'IT-VINE-FLAVESCENCE']),
    ('IT-VENETO-SFR', 'Regione Veneto — Servizio fitosanitario',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'IT', 'Veneto',
     'https://www.regione.veneto.it/web/fitosanitario/bollettini',
     ['IT-VINE-FLAVESCENCE', 'IT-DURUM_WHEAT-FUSARIUM']),
    ('IT-EMILIA-BOLL', 'Regione Emilia-Romagna — bollettini di produzione integrata',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'IT', 'Emilia-Romagna',
     'https://agricoltura.regione.emilia-romagna.it/fitosanitario/'
     'difesa-sostenibile/bollettini',
     ['IT-DURUM_WHEAT-FUSARIUM', 'IT-VINE-FLAVESCENCE']),
    ('IT-PIEMONTE-SFR', 'Regione Piemonte — Settore fitosanitario',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'IT', 'Piemonte',
     'https://www.regione.piemonte.it/web/temi/agricoltura/agricoltura-sostenibile/'
     'servizio-fitosanitario',
     ['IT-VINE-FLAVESCENCE']),
    ('IT-LAMMA', 'Consorzio LaMMA — Bollettino Frumento (Regione Toscana)',
     'EXPERIMENTAL_STATION', 'IT', 'Toscana',
     'https://www.lamma.toscana.it/agrometeo/bollettino-frumento',
     ['IT-DURUM_WHEAT-FUSARIUM']),
    ('IT-AGRONOTIZIE', 'AgroNotizie (Image Line) — imprensa técnica',
     'TECHNICAL_PRESS', 'IT', 'Italia',
     'https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/',
     ['IT-DURUM_WHEAT-FUSARIUM', 'IT-VINE-FLAVESCENCE']),
    ('IT-HORTA-GRANO', 'Horta srl — grano.net',
     'TECHNICAL_ORGANIZATION', 'IT', 'Italia', 'https://www.grano.net/',
     ['IT-DURUM_WHEAT-FUSARIUM']),

    # ── FR ───────────────────────────────────────────────────────────────────────
    # O BSV — Bulletin de Santé du Végétal — é a fonte territorial francesa por
    # excelência: um boletim por região e por cultura, assinado pelo serviço regional.
    # O acervo já registra que o Agreste e o BSV apareceram BLOQUEADOS numa rodada
    # anterior. Isso é motivo para MEDIR de novo daqui, não para desistir: bloqueio de
    # borda depende do IP, e esta máquina é residencial.
    ('FR-BSV-NA', 'Bulletin de Santé du Végétal — Nouvelle-Aquitaine',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'FR', 'Nouvelle-Aquitaine',
     'https://nouvelle-aquitaine.chambres-agriculture.fr/productions-techniques/'
     'bulletins-techniques/bulletin-de-sante-du-vegetal/',
     ['FR-VINE-DOWNY_MILDEW', 'FR-CEREAL-SEPTORIA']),
    ('FR-BSV-OCC', 'Bulletin de Santé du Végétal — Occitanie',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'FR', 'Occitanie',
     'https://occitanie.chambre-agriculture.fr/productions-techniques/'
     'bulletins-de-sante-du-vegetal/',
     ['FR-VINE-DOWNY_MILDEW', 'FR-CEREAL-SEPTORIA']),
    ('FR-BSV-GE', 'Bulletin de Santé du Végétal — Grand Est',
     'REGIONAL_PHYTOSANITARY_SERVICE', 'FR', 'Grand Est',
     'https://grandest.chambre-agriculture.fr/productions-techniques/'
     'bulletins-techniques-et-de-sante-du-vegetal/',
     ['FR-VINE-DOWNY_MILDEW', 'FR-CEREAL-SEPTORIA']),
    ('FR-VIGNEVIN', 'IFV — Institut Français de la Vigne et du Vin',
     'TECHNICAL_ORGANIZATION', 'FR', 'France', 'https://www.vignevin.com/',
     ['FR-VINE-DOWNY_MILDEW']),
    ('FR-ARVALIS', 'ARVALIS — Institut du végétal',
     'TECHNICAL_ORGANIZATION', 'FR', 'France', 'https://www.arvalis.fr/',
     ['FR-CEREAL-SEPTORIA']),
    ('FR-TERRENET', 'Terre-net — imprensa técnica agrícola',
     'TECHNICAL_PRESS', 'FR', 'France', 'https://www.terre-net.fr/',
     ['FR-CEREAL-SEPTORIA']),
    ('FR-VITISPHERE', 'Vitisphere — imprensa técnica da vinha',
     'TECHNICAL_PRESS', 'FR', 'France', 'https://www.vitisphere.com/',
     ['FR-VINE-DOWNY_MILDEW']),
]


def _buscar(url, timeout=35):
    """→ (status, corpo, tipo, motivo). NUNCA levanta: bloqueio é ESTADO da fonte."""
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'es,it,fr,en;q=0.8'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            bruto = r.read(1200000)
            tipo = r.headers.get('Content-Type', '')
            return r.status, bruto, tipo, None
    except urllib.error.HTTPError as e:
        # 403 NÃO É "empresa silenciosa". É estado da fonte, e fica registrado como tal.
        return e.code, b'', '', 'HTTP %d' % e.code
    except Exception as e:                                    # noqa: BLE001
        return None, b'', '', '%s' % type(e).__name__


def _curl(url, timeout=35):
    """Segunda tentativa por curl. Medido nesta casa: a mesma URL deu 403 num cliente e
    200 no outro, e o bloqueio era intermitente. Um cliente só mede o cliente."""
    try:
        r = subprocess.run(
            ['curl', '-sSL', '--max-time', str(timeout), '-A', UA,
             '-H', 'Accept-Language: es,it,fr,en;q=0.8',
             '-w', '\n__HTTP__%{http_code}', url],
            capture_output=True, timeout=timeout + 10)
        saida = r.stdout.decode('utf-8', 'replace')
        m = re.search(r'__HTTP__(\d+)$', saida)
        codigo = int(m.group(1)) if m else None
        return codigo, saida[:m.start()].encode() if m else b'', '', None
    except Exception as e:                                    # noqa: BLE001
        return None, b'', '', type(e).__name__


# A ORDEM DAS ALTERNATIVAS É O CONSERTO — 2026-09-04
# ---------------------------------------------------
# A versão anterior escrevia o dia como `(0?[1-9]|[12]\d|3[01])`. Alternância em regex é
# *leftmost-first*: contra "24", o motor casa `0?[1-9]` com o "2", e como nada depois exige
# retrocesso, ele PARA ALI. O dia virava o dígito das dezenas — em silêncio, sem erro:
#
#     datas_no_texto('2026-08-24')  ->  2026-08-02
#     datas_no_texto('2026-12-25')  ->  2026-12-02
#
# Medido: 257 das 365 datas ISO de 2026 voltavam erradas (70%). Em `dd/mm/aaaa`, nenhuma —
# porque ali o `[-/]` seguinte forçava o retrocesso que o formato ISO não força.
#
#     O ERRO TINHA DIREÇÃO: sempre para trás, sempre para o começo do mês.
#
# Isso não é ruído. Uma camada que mede FRESCOR com data truncada faz toda fonte parecer
# mais velha do que é — e a conclusão errada ("essa fonte está parada") é justamente a que
# o número existe para evitar.
#
# O conserto é pôr as alternativas longas primeiro, para que a mais específica ganhe.
DATA = re.compile(
    r'(20\d{2})[-/](1[0-2]|0?[1-9])[-/](3[01]|[12]\d|0?[1-9])'
    r'|(3[01]|[12]\d|0?[1-9])[-/](1[0-2]|0?[1-9])[-/](20\d{2})')


def datas_no_texto(texto):
    """Datas que o TEXTO nomeia. Nada é inferido de cabeçalho HTTP."""
    fora = set()
    for m in DATA.finditer(texto):
        try:
            if m.group(1):
                d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            else:
                d = datetime.date(int(m.group(6)), int(m.group(5)), int(m.group(4)))
        except ValueError:
            continue
        if datetime.date(2015, 1, 1) <= d <= datetime.date(2027, 12, 31):
            fora.add(d)
    return sorted(fora)


# Palavras que nomeiam um boletim nas quatro línguas do corpus. Servem para ACHAR o
# caminho certo dentro do domínio, não para julgar conteúdo.
PALAVRAS_BOLETIM = ('bollettin', 'boletin', 'boletín', 'bulletin', 'aviso', 'avvis',
                    'fitosanitar', 'fitosanitari', 'sante-du-vegetal', 'bsv',
                    'difesa', 'sanidad-vegetal', 'sanitat-vegetal')


def _raiz(url):
    m = re.match(r'(https?://[^/]+)', url)
    return m.group(1) + '/' if m else url


def _links_de_boletim(texto, base):
    """Links da página que se anunciam como boletim. Derivado, não digitado."""
    fora = []
    for m in re.finditer(r'href="([^"#]+)"[^>]*>(.{0,140}?)</a>', texto,
                         re.I | re.S):
        href, rotulo = m.group(1), re.sub(r'<[^>]+>', ' ', m.group(2))
        alvo = (href + ' ' + rotulo).lower()
        if any(p in alvo for p in PALAVRAS_BOLETIM):
            if href.startswith('/'):
                href = _raiz(base).rstrip('/') + href
            if href.startswith('http'):
                fora.append((href, ' '.join(rotulo.split())[:90]))
    vistos, unicos = set(), []
    for h, r in fora:
        if h not in vistos:
            vistos.add(h)
            unicos.append({'URL': h, 'LABEL': r})
    return unicos[:12]


def sondar_uma(chave, nome, tipo, pais, mandato, url, recortes, hoje):
    """Tenta o caminho declarado; se ele falhar, tenta a RAIZ do domínio.

    POR QUE A SEGUNDA TENTATIVA EXISTE, e ela nasceu de um erro meu.
    A primeira rodada devolveu 404 para 8 das 22 fontes, e eu quase reportei isso como
    "fonte indisponível". Testando a raiz, `agronotizie.imagelinenetwork.com` e
    `lamma.toscana.it` responderam **200**: o que estava errado era o CAMINHO que eu tinha
    digitado, não o site.

        404 NA MINHA URL != FONTE INEXISTENTE.

    Quando a raiz abre, a sonda também lista os links que se anunciam como boletim. Assim
    o caminho certo é DESCOBERTO da própria fonte em vez de adivinhado por mim de novo.
    """
    status, bruto, ctype, motivo = _buscar(url)
    via, url_usada, caminho_declarado_ok = 'urllib', url, status == 200
    if status != 200:
        s2, b2, c2, m2 = _curl(url)
        if s2 == 200:
            status, bruto, ctype, motivo, via = s2, b2, c2, None, 'curl'
            caminho_declarado_ok = True
    achados = []
    if status != 200 and _raiz(url) != url:
        for tentativa in (_buscar, _curl):
            s3, b3, c3, m3 = tentativa(_raiz(url))
            if s3 == 200:
                status, bruto, ctype, motivo = s3, b3, c3, None
                via = 'raiz/%s' % ('curl' if tentativa is _curl else 'urllib')
                url_usada = _raiz(url)
                achados = _links_de_boletim(
                    b3.decode('utf-8', 'replace'), _raiz(url))
                break
    texto = bruto.decode('utf-8', 'replace')
    # PDF é formato de conteúdo, não falha. Muitos boletins regionais SÓ existem em PDF.
    pdfs = len(re.findall(r'href="[^"]+\.pdf', texto, re.I))
    formato = ('PDF_LINKS' if pdfs >= 3 else
               'HTML' if 'text/html' in (ctype or '') or '<html' in texto[:2000].lower()
               else NAO_SEI)
    feed = bool(re.search(r'\.(rss|xml)"|application/rss', texto, re.I))
    datas = datas_no_texto(texto)
    d30 = sum(1 for d in datas if (hoje - d).days <= 30)
    d90 = sum(1 for d in datas if (hoje - d).days <= 90)
    d180 = sum(1 for d in datas if (hoje - d).days <= 180)
    return {
        'SOURCE_ENTITY_ID': chave, 'SOURCE_NAME': nome, 'SOURCE_TYPE': tipo,
        'SOURCE_COUNTRY': pais, 'SOURCE_REGION': mandato,
        'MANDATE_GEOGRAPHY': mandato,
        'PUBLIC_URL': url, 'URL_FETCHED': url_usada, 'SERVES_CASES': recortes,
        'DECLARED_PATH_OK': caminho_declarado_ok,
        'BULLETIN_LINKS_FOUND': achados,
        'HTTP_STATUS': status if status is not None else NAO_SEI,
        'FETCHED_VIA': via if status == 200 else NAO_SEI,
        'REACHABLE': status == 200,
        'FAILURE_REASON': motivo or (None if status == 200 else 'sem resposta'),
        'CONTENT_FORMAT': formato if status == 200 else NAO_SEI,
        'PDF_LINKS_ON_PAGE': pdfs if status == 200 else NAO_SEI,
        'HAS_FEED': feed if status == 200 else NAO_SEI,
        'ACCESS_ROUTE': ('FEED' if feed else 'PDF_DOWNLOAD' if formato == 'PDF_LINKS'
                         else 'HTML_DIRECT' if formato == 'HTML' else NAO_SEI),
        'LATEST_ITEM_DATE': datas[-1].isoformat() if datas else NAO_SEI,
        'DATES_ON_PAGE': len(datas),
        'ITEMS_LAST_30D': d30, 'ITEMS_LAST_90D': d90, 'ITEMS_LAST_180D': d180,
        'PAGE_BYTES': len(bruto),
        # Vivo é sobre a JANELA, não sobre o arquivo. Fonte com muita data antiga e nenhuma
        # recente é arquivo — e o piloto anterior mostrou como é fácil confundir os dois.
        'LIVENESS': ('LIVE_30D' if d30 else 'LIVE_90D' if d90 else
                     'LIVE_180D' if d180 else 'ARCHIVE_OR_UNKNOWN'),
    }


def sondar():
    hoje = datetime.date.today()
    fora = []
    for f in FONTES:
        r = sondar_uma(*f, hoje=hoje)
        fora.append(r)
        print('%-18s %-5s %-12s %-9s ult=%-11s 30/90/180=%d/%d/%d  %s'
              % (r['SOURCE_ENTITY_ID'], str(r['HTTP_STATUS'])[:5],
                 str(r['CONTENT_FORMAT'])[:12], r['LIVENESS'][:9],
                 str(r['LATEST_ITEM_DATE'])[:11],
                 r['ITEMS_LAST_30D'] if r['REACHABLE'] else 0,
                 r['ITEMS_LAST_90D'] if r['REACHABLE'] else 0,
                 r['ITEMS_LAST_180D'] if r['REACHABLE'] else 0,
                 r['FAILURE_REASON'] or ''))
    os.makedirs(SAIDA, exist_ok=True)
    corpo = {
        'SOURCE_ID': 'TERRITORIAL/INVENTARIO-DE-FONTES',
        'DATASET_OWNER': 'EARLY_SIGNAL_EAME',
        'MISSION_ID': '16-ROTA-TERRITORIAL',
        'source': 'sondagem pública das fontes candidatas — nenhuma coleta de conteúdo',
        'SOURCE_LOCATION': 'ES, IT, FR',
        'FACT_LOCATION': 'n/a — descreve a fonte, não o fato',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': hoje.isoformat(), 'CAPTURED_AT': hoje.isoformat(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_MEDE': 'se a fonte existe, abre, publica, e publicou RECENTEMENTE',
        'O_QUE_ISTO_NAO_MEDE': [
            'não mede se o conteúdo é do recorte — isso é a fase de coleta',
            'não mede localidade do fato: mandato da fonte não é lugar do fato',
            'as datas são as que a PÁGINA nomeia; página sem data não é fonte sem data',
        ],
        'LEI': ('403 não é fonte silenciosa; é estado da fonte. Falha de leitura não é '
                'zero. Duas tentativas com clientes diferentes, porque um cliente só '
                'mede o cliente.'),
        'SOURCES_ATTEMPTED': len(fora),
        'SOURCES_REACHABLE': sum(1 for r in fora if r['REACHABLE']),
        'SOURCES': fora,
    }
    caminho = os.path.join(SAIDA, 'INVENTARIO-DE-FONTES.json')
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\ntentadas %d · alcançadas %d · gravado em %s'
          % (len(fora), corpo['SOURCES_REACHABLE'],
             os.path.relpath(caminho, ROOT).replace('\\', '/')))
    return 0


def resumo():
    with open(os.path.join(SAIDA, 'INVENTARIO-DE-FONTES.json'), encoding='utf-8') as f:
        d = json.load(f)
    porviv = {}
    for r in d['SOURCES']:
        porviv[r['LIVENESS']] = porviv.get(r['LIVENESS'], 0) + 1
    print('%d fontes · alcançadas %d · %s'
          % (d['SOURCES_ATTEMPTED'], d['SOURCES_REACHABLE'], porviv))
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'sondar'
    raise SystemExit({'sondar': sondar, 'resumo': resumo}[cmd]())
