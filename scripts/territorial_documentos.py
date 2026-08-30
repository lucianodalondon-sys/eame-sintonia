#!/usr/bin/env python3
"""
SEGUNDA PASSAGEM — o CORPO dos boletins, não o menu do site.

    python3 scripts/territorial_documentos.py coletar

POR QUE ESTA PASSAGEM EXISTE: EU JULGUEI A ROTA PELO MENU DO SITE
------------------------------------------------------------------
A primeira passagem leu a LISTAGEM e pegou todo `<a>` cujo texto citava uma cultura. O
resultado, medido, foi 62 "itens" — e a leitura um a um mostrou o que eles eram:

    "Videointerpretación"          menu de acessibilidade
    "Sectores de actividad"        menu institucional
    "Registro Oficial de ..."      página de serviço

Com esse material, `ITEMS_WITH_ISSUE` deu 6% e `COMPLETE_KEY` deu 0% — e eu quase reportei
isso como reprovação da ROTA TERRITORIAL. Não era. Era reprovação do meu extrator.

    JULGAR A FONTE PELO MENU DO SITE É O MESMO ERRO DE LER O VÍDEO PELO TÍTULO.

É literalmente a lição que a rodada anterior já tinha pago — "descrição sozinha não é
conteúdo técnico" — aplicada agora contra mim mesmo, na direção oposta.

O QUE MUDA
-----------
Só entra o que TEM CARA DE DOCUMENTO: PDF, ou URL com data no caminho, ou link cujo rótulo
se anuncia como boletim numerado. E o texto medido é o CORPO do documento, não o rótulo do
link. Cultura, problema, tipo de observação e lugar passam a sair de onde eles realmente
estão escritos.

O QUE NÃO MUDA
---------------
A regra de herança territorial, os pisos, os seis recortes e a proibição de inferir lugar
por idioma. Corrigir o extrator não é afrouxar critério — é parar de medir a coisa errada.
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
import fonte_territorial as ft       # noqa: E402
import sensor_territorial as st      # noqa: E402

TER = os.path.join(ROOT, 'data', 'samples', 'TERRITORIAL')
RAW = os.path.join(ROOT, 'data', 'raw', 'TERRITORIAL')
NAO_SEI = 'NOT_KNOWN'

# Navegação que NUNCA é boletim. Lista curta e declarada — ela existe porque cada um
# destes apareceu como "item" na primeira passagem.
LIXO = ('videointerpretacion', 'aviso legal', 'sectores de actividad', 'accesibilidad',
        'mapa web', 'contacto', 'cookies', 'privacidad', 'suscri', 'newsletter',
        'registro oficial', 'sede electr', 'transparencia', 'buscador', 'portada')


def _e_documento(url, rotulo):
    """→ (sim, motivo). Documento é PDF, URL com data, ou boletim numerado."""
    u, r = url.lower(), rotulo.lower()
    if any(t in r for t in LIXO):
        return False, 'rótulo de navegação'
    if u.endswith('.pdf') or '.pdf?' in u:
        return True, 'PDF'
    if re.search(r'/20\d{2}/\d{1,2}/\d{1,2}/', u):
        return True, 'URL com data'
    if re.search(r'(n[.°º]?\s*\d+|num\.?\s*\d+|\bn\d+\b)', r) and \
            any(p in r for p in st.MARCA_BOLETIM):
        return True, 'boletim numerado no rótulo'
    if re.search(r'20\d{2}', u) and any(p in u for p in st.MARCA_BOLETIM):
        return True, 'caminho de boletim com ano'
    return False, 'não se anuncia como documento'


def _baixar(url, timeout=45):
    req = urllib.request.Request(url, headers={'User-Agent': ft.UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(6000000), r.headers.get('Content-Type', ''), None
    except urllib.error.HTTPError as e:
        return e.code, b'', '', 'HTTP %d' % e.code
    except Exception as e:                                    # noqa: BLE001
        try:
            p = subprocess.run(['curl', '-sSL', '--max-time', str(timeout),
                                '-A', ft.UA, url], capture_output=True,
                               timeout=timeout + 10)
            if p.returncode == 0 and p.stdout:
                return 200, p.stdout, '', None
        except Exception:                                     # noqa: BLE001
            pass
        return None, b'', '', type(e).__name__


def _texto(bruto, ctype, url):
    """Texto do documento. PDF pela rota da casa; HTML por remoção de marcação."""
    if bruto[:5] == b'%PDF-' or 'pdf' in (ctype or '').lower() or url.lower().endswith('.pdf'):
        caminho = os.path.join(RAW, re.sub(r'\W+', '_', url)[-90:] + '.pdf')
        os.makedirs(RAW, exist_ok=True)
        with open(caminho, 'wb') as f:
            f.write(bruto)
        try:
            import pdf_text
            for nome in ('extract', 'texto', 'extrair', 'text_from_pdf', 'main'):
                fn = getattr(pdf_text, nome, None)
                if callable(fn):
                    try:
                        return str(fn(caminho))[:200000], 'PDF/%s' % nome, caminho
                    except Exception:                          # noqa: BLE001
                        continue
        except Exception:                                      # noqa: BLE001
            pass
        return '', 'PDF_NAO_EXTRAIDO', caminho
    html = bruto.decode('utf-8', 'replace')
    html = re.sub(r'(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>', ' ', html)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html))[:200000], 'HTML', None


def coletar():
    hoje = datetime.date.today()
    with open(os.path.join(TER, 'INVENTARIO-DE-FONTES.json'), encoding='utf-8') as f:
        inv = json.load(f)
    fontes = [s for s in inv['SOURCES'] if s['REACHABLE']]
    itens, tentados, baixados = [], 0, 0
    for fo in fontes:
        s, html, motivo = st._buscar(fo['URL_FETCHED'])
        if s != 200:
            continue
        candidatos = []
        for b in st._itens_da_pagina(html, fo['URL_FETCHED'], hoje):
            ok, por = _e_documento(b['URL'], b['TITLE'])
            if ok:
                candidatos.append(dict(b, WHY_DOC=por))
        # Teto por fonte: primeiro lote pequeno, como o contrato manda.
        candidatos = candidatos[:8]
        if not candidatos:
            print('  %-18s 0 documentos na listagem' % fo['SOURCE_ENTITY_ID'])
            continue
        n_ok = 0
        for c in candidatos:
            tentados += 1
            st_, bruto, ctype, err = _baixar(c['URL'])
            if st_ != 200 or not bruto:
                continue
            texto, via, rawpath = _texto(bruto, ctype, c['URL'])
            if not texto.strip():
                continue
            baixados += 1
            crops, issues = st.crop_issue(c['TITLE'], texto)
            if not crops and not issues:
                continue
            pais, regiao, base, ev = st.lugar_do_fato(fo, c['TITLE'], texto)
            tipo, tev = st.classificar(c['TITLE'], texto)
            datas = ft.datas_no_texto(texto[:20000])
            pub = c['DATE'] if c['DATE'] != NAO_SEI else (
                datas[-1].isoformat() if datas else NAO_SEI)
            n_ok += 1
            itens.append({
                'ITEM_ID': '%s::%s' % (fo['SOURCE_ENTITY_ID'],
                                       re.sub(r'\W+', '-', c['URL'])[-60:]),
                'DATASET_OWNER': 'EARLY_SIGNAL_EAME', 'MISSION_ID': st.MISSION,
                'BATCH_ID': 'TERRITORIAL-DOCS',
                'SOURCE_ENTITY_ID': fo['SOURCE_ENTITY_ID'],
                'SOURCE_NAME': fo['SOURCE_NAME'], 'SOURCE_TYPE': fo['SOURCE_TYPE'],
                'SOURCE_URL': c['URL'],
                'SOURCE_COUNTRY': fo['SOURCE_COUNTRY'],
                'SOURCE_REGION': fo['SOURCE_REGION'],
                'MANDATE_GEOGRAPHY': fo['MANDATE_GEOGRAPHY'],
                'PUBLISHED_AT': pub, 'CAPTURED_AT': hoje.isoformat(),
                'COUNTRY_OF_FACT': pais, 'REGION_OF_FACT': regiao,
                'LOCALITY_BASIS': base, 'LOCALITY_EVIDENCE': ev,
                'CROP': crops or NAO_SEI, 'ISSUE': issues or NAO_SEI,
                'OBSERVATION_TYPE': tipo, 'OBSERVATION_TYPE_EVIDENCE': tev,
                'OBSERVATION_TEXT': c['TITLE'],
                'DOCUMENT_CHARS': len(texto),
                'DOCUMENT_EXCERPT': texto[:1500],
                'WHY_DOCUMENT': c['WHY_DOC'],
                # Boletim de serviço fitossanitário regional é observação PRÓPRIA da
                # rede dele: é para isso que a rede existe. Imprensa técnica relata o
                # que outros observaram, e por isso não herda originalidade.
                'ORIGINAL_OBSERVATION': (
                    'YES' if fo['SOURCE_TYPE'] in st.TIPOS_QUE_HERDAM else NAO_SEI),
                'ORIGINAL_OBSERVATION_OWNER': fo['SOURCE_NAME'],
                'EVIDENCE_OF_ORIGINALITY': (
                    'boletim publicado pelo próprio serviço com mandato sobre o '
                    'território' if fo['SOURCE_TYPE'] in st.TIPOS_QUE_HERDAM
                    else 'veículo que relata observação de terceiros'),
                'PROVENANCE': {'ROUTE': fo['ACCESS_ROUTE'], 'TOOL': 'HTTP_DIRECT',
                               'APIFY': False, 'EXTRACTION': via,
                               'RAW_PATH': (os.path.relpath(rawpath, ROOT).replace('\\', '/')
                                            if rawpath else None),
                               'LISTING_URL': fo['URL_FETCHED']},
            })
        print('  %-18s %2d documentos -> %2d do recorte' % (
            fo['SOURCE_ENTITY_ID'], len(candidatos), n_ok))
    corpo = {
        'SOURCE_ID': 'TERRITORIAL/DOCUMENTOS',
        'DATASET_OWNER': 'EARLY_SIGNAL_EAME', 'MISSION_ID': st.MISSION,
        'source': 'corpo dos boletins, baixado por HTTP direto — zero Apify',
        'SOURCE_LOCATION': 'ES, IT, FR', 'FACT_LOCATION': 'ver por item',
        'ORIGINAL_LANGUAGE': 'multi', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE',
        'captured_at': hoje.isoformat(), 'CAPTURED_AT': hoje.isoformat(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'DOCUMENTS_TRIED': tentados, 'DOCUMENTS_FETCHED': baixados,
        'ITEMS_COUNT': len(itens),
        'POR_QUE_ESTA_PASSAGEM': ('a primeira leu a listagem e capturou menu de site. '
                                  'Julgar a fonte pelo menu é o mesmo erro de ler o '
                                  'vídeo pelo título.'),
        'ITEMS': itens,
    }
    with open(os.path.join(TER, 'DOCUMENTOS.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('\ndocumentos tentados %d · baixados %d · itens do recorte %d'
          % (tentados, baixados, len(itens)))
    return 0


if __name__ == '__main__':
    raise SystemExit(coletar())
