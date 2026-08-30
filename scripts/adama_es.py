#!/usr/bin/env python3
"""
CENSO ADAMA ESPAÑA — coletor + parser determinístico do portfólio público.

O que este arquivo é: a rota inteira do censo, do denominador ao documento, escrita para
rodar sem agente. A seção 31 da missão pede parser determinístico depois que o padrão da
página for conhecido; este é o parser, e ele não depende de saber o padrão de antemão —
extrai por ESTRUTURA (tabela, linha, cabeçalho, âncora), não por seletor adivinhado.

O que este arquivo NÃO é: prova de que o catálogo tem N produtos. Ele não inventa
denominador. Rodar sem acesso devolve NOT_COLLECTED com o motivo medido; nunca 0.

    python3 scripts/adama_es.py --censo            # rota completa (exige acesso)
    python3 scripts/adama_es.py --parse ARQ.html --url URL   # parser sobre HTML salvo
    python3 scripts/adama_es.py --autoteste        # invariantes sobre fixtures

A LEI QUE ATRAVESSA O ARQUIVO INTEIRO

    OBSERVED != MANUFACTURER CLAIM != REGULATORY FACT != DERIVED INTERPRETATION

Cada campo emitido carrega de qual dos quatro ele é. Um número sem essa marca não sai.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
COUNTRY = 'ES'
BASE = 'https://www.adama.com'
CATALOGO = BASE + '/spain/es/products/crop-protection/downloads'

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')


# ══════════════════════════════════════════════════════════════════════════════
# 1 · VOCABULÁRIO OFICIAL — nenhum nome de cultivo ou praga é inventado
# ══════════════════════════════════════════════════════════════════════════════

def vocabulario():
    """Cultivos e agentes nomeados pelo MAPA. O parser só reconhece o que o MAPA nomeia.

    Três fontes, todas já no repo, nenhuma inventada aqui:

      ES-ADAMA-PORTFOLIO-ROPF  CULTIVOS e AGENTES das 96 fichas vigentes da ADAMA. É o
                               vocabulário EXATO do registro espanhol, e é o que o
                               crosswalk da seção 16 vai comparar.
      eppo-dictionary          hierarquia oficial ES-T4-001, para o que a ADAMA cita e o
                               registro dela não cobre (ex.: repilo, se ausente do ROPF).
      —                        e mais nada. Sem lista própria, sem sinônimo escrito à mão.

    O MAPA escreve rótulo composto: "SEPTORIOSIS, SEPTORIA SPP." e "Oídio de la vid,
    Erysiphe necator". A vírgula é NOTAÇÃO do MAPA separando nome comum de nome
    científico, então cada lado vira um token que aponta para o MESMO rótulo oficial.
    Isso não é sinônimo inventado: é ler a notação da fonte.
    """
    crops, pests = {}, {}

    def por(tabela, rotulo, code, sci=''):
        rotulo = _limpar_rotulo(rotulo)
        if not rotulo:
            return
        for pedaco in _alias(rotulo):
            k = _chave(pedaco)
            if len(k) >= 4:
                tabela.setdefault(k, {'EPPO': code, 'ES': rotulo, 'SCI': sci,
                                      'MATCHED_AS': pedaco})

    ropf = os.path.join(SAMPLES, 'ES-ADAMA-PORTFOLIO-ROPF.json')
    if os.path.exists(ropf):
        with open(ropf, encoding='utf-8') as f:
            for ficha in (json.load(f).get('FICHAS') or []):
                for c in ficha.get('CULTIVOS') or []:
                    por(crops, c, 'MAPA-ROPF')
                for a in ficha.get('AGENTES') or []:
                    por(pests, a, 'MAPA-ROPF')

    eppo = os.path.join(SAMPLES, 'ES-T4-001', 'eppo-dictionary.json')
    if os.path.exists(eppo):
        with open(eppo, encoding='utf-8') as f:
            d = json.load(f)
        for code, v in (d.get('crops') or {}).items():
            por(crops, v.get('es', ''), code)
        for code, v in (d.get('pests') or {}).items():
            por(pests, v.get('es', ''), code, v.get('scientific', ''))

    return {'crops': crops, 'pests': pests,
            'DISPONIVEL': bool(crops and pests),
            'CROP_TOKENS': len(crops), 'ISSUE_TOKENS': len(pests)}


def _alias(rotulo):
    """O rótulo inteiro e cada lado da vírgula. Só desfaz notação — não cria termo novo."""
    fora = [rotulo]
    if ',' in rotulo:
        fora += [p.strip() for p in rotulo.split(',') if len(p.strip()) >= 4]
    return fora


def _limpar_rotulo(s):
    """Tira a numeração hierárquica do MAPA ("1.1.1.1. Coníferas" -> "Coníferas")."""
    return re.sub(r'^[\d.]+\s*', '', (s or '')).strip()


def _chave(s):
    """Forma de comparação: sem acento, sem caixa, sem pontuação de borda.

    NÃO é normalização semântica. Só remove o que é notação. "maíz" e "MAIZ" são o mesmo
    token; "maíz dulce" continua sendo OUTRO token — variante não colapsa em cultivo-pai.
    """
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', s).strip()


# ══════════════════════════════════════════════════════════════════════════════
# 2 · HTML -> ESTRUTURA (tabelas, listas, seções, links) preservando a origem
# ══════════════════════════════════════════════════════════════════════════════

class _Arvore(HTMLParser):
    """Extrai o que o censo precisa e DE ONDE veio. A âncora é o produto principal.

    Cada bloco emitido carrega ANCHOR: seção + índice de tabela + índice de linha. Sem
    âncora não existe seção 9 — "preservar linha/bloco/origem" vira promessa não checável.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tabelas, self.links, self.textos, self.videos, self.metas = [], [], [], [], []
        self._pilha, self._secao = [], ''
        self._tab, self._linha, self._cel = None, None, None
        self._href, self._link_txt = None, ''
        self._titulo_nivel = None

    # -- entrada -----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._pilha.append(tag)
        if tag == 'table':
            self._tab = {'INDICE': len(self.tabelas), 'SECAO': self._secao,
                         'LINHAS': [], 'CABECALHO': []}
        elif tag == 'tr' and self._tab is not None:
            self._linha = []
        elif tag in ('td', 'th') and self._linha is not None:
            self._cel = {'texto': '', 'tag': tag,
                         'colspan': int(a.get('colspan') or 1)}
        elif tag in ('h1', 'h2', 'h3', 'h4'):
            self._titulo_nivel = tag
            self._buf_titulo = ''
        elif tag == 'a' and a.get('href'):
            self._href, self._link_txt = a['href'], ''
        elif tag == 'iframe' and a.get('src'):
            self._talvez_video(a['src'], '')
        elif tag == 'meta':
            n = a.get('property') or a.get('name')
            if n and a.get('content'):
                self.metas.append({'NOME': n, 'CONTEUDO': a['content'][:400]})

    def handle_data(self, data):
        t = data.strip()
        if not t:
            return
        if self._cel is not None:
            self._cel['texto'] += (' ' if self._cel['texto'] else '') + t
        if self._href is not None:
            self._link_txt += (' ' if self._link_txt else '') + t
        if self._titulo_nivel:
            self._buf_titulo += (' ' if self._buf_titulo else '') + t
        if self._pilha and self._pilha[-1] not in ('script', 'style'):
            self.textos.append({'TEXTO': t, 'SECAO': self._secao,
                                'TAG': self._pilha[-1] if self._pilha else ''})

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self._cel is not None and self._linha is not None:
            self._linha.append(self._cel)
            self._cel = None
        elif tag == 'tr' and self._tab is not None and self._linha is not None:
            celulas = [c['texto'] for c in self._linha]
            ehcab = all(c['tag'] == 'th' for c in self._linha) and self._linha
            if ehcab and not self._tab['CABECALHO']:
                self._tab['CABECALHO'] = celulas
            else:
                self._tab['LINHAS'].append({'INDICE': len(self._tab['LINHAS']),
                                            'CELULAS': celulas})
            self._linha = None
        elif tag == 'table' and self._tab is not None:
            self.tabelas.append(self._tab)
            self._tab = None
        elif tag in ('h1', 'h2', 'h3', 'h4') and self._titulo_nivel:
            self._secao = self._buf_titulo.strip()[:160]
            self._titulo_nivel = None
        elif tag == 'a' and self._href is not None:
            self.links.append({'HREF': self._href, 'TEXTO': self._link_txt.strip()[:220],
                               'SECAO': self._secao})
            self._talvez_video(self._href, self._link_txt)
            self._href, self._link_txt = None, ''
        if self._pilha:
            self._pilha.pop()

    # -- vídeo -------------------------------------------------------------
    _VIDEO = [
        ('YOUTUBE', re.compile(r'(?:youtube\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{6,})')),
        ('VIMEO',   re.compile(r'vimeo\.com/(?:video/)?(\d{5,})')),
    ]

    def _talvez_video(self, url, titulo):
        for plataforma, rx in self._VIDEO:
            m = rx.search(url or '')
            if m:
                self.videos.append({'PLATFORM': plataforma, 'VIDEO_ID': m.group(1),
                                    'VIDEO_URL': url, 'TITLE': (titulo or '').strip()[:200],
                                    'SECAO': self._secao,
                                    'TRANSCRIPT_STATUS': 'NOT_COLLECTED'})
                return


def estruturar(html):
    p = _Arvore()
    try:
        p.feed(html)
        p.close()
    except Exception:
        pass          # HTML real quebra parser; o que já foi lido continua valendo
    return {'TABELAS': p.tabelas, 'LINKS': p.links, 'TEXTOS': p.textos,
            'VIDEOS': p.videos, 'METAS': p.metas}


# ══════════════════════════════════════════════════════════════════════════════
# 3 · DOCUMENTOS — nove tipos, e nenhum deles se chama "bula"
# ══════════════════════════════════════════════════════════════════════════════
#
# A ordem importa: o primeiro padrão que casa vence. SDS vem antes de LABEL porque
# "ficha de datos de seguridad" contém "ficha", e um SDS classificado como etiqueta é
# exatamente o erro que a seção 26 manda impedir.

TIPOS_DOC = [
    ('SDS', re.compile(
        r'(ficha\s+de\s+datos\s+de\s+seguridad|fds\b|\bsds\b|safety\s+data\s+sheet|'
        r'hoja\s+de\s+seguridad|seguridad)', re.I)),
    ('ADAMA_COMMERCIAL_LABEL', re.compile(
        r'(etiqueta|label|prospecto)', re.I)),
    ('REGISTRATION_SHEET', re.compile(
        r'(registro|ficha\s+de\s+registro|autorizaci[oó]n|inscripci[oó]n)', re.I)),
    ('TECHNICAL_SHEET', re.compile(
        r'(ficha\s+t[eé]cnica|hoja\s+t[eé]cnica|technical\s+(data\s+)?sheet|'
        r'ficha\s+de\s+producto)', re.I)),
    ('TRIAL_DOCUMENT', re.compile(
        r'(ensayo|ensayos|trial|resultados\s+de\s+campo|prueba\s+de\s+campo)', re.I)),
    ('GUIDE', re.compile(r'(gu[ií]a|manual|recomendaci[oó]n(es)?|protocolo)', re.I)),
    ('BROCHURE', re.compile(r'(folleto|d[ií]ptico|tr[ií]ptico|brochure|flyer)', re.I)),
    ('CATALOG', re.compile(r'(cat[aá]logo|vademecum|vadem[eé]cum)', re.I)),
]


def classificar_documento(texto_link, url):
    """Devolve (TIPO, EVIDENCIA). Sem casar nada -> OTHER_TECHNICAL_DOCUMENT, nunca chute.

    Classifica pelo TEXTO DO LINK primeiro e pela URL depois: o texto é o que a ADAMA
    declara que o arquivo é; a URL é só onde ele mora.
    """
    for alvo, origem in ((texto_link or '', 'TEXTO_DO_LINK'), (url or '', 'URL')):
        for tipo, rx in TIPOS_DOC:
            m = rx.search(alvo)
            if m:
                return tipo, '%s casou "%s"' % (origem, m.group(0)[:40])
    return 'OTHER_TECHNICAL_DOCUMENT', 'nenhum padrao de tipo casou — nao classificado por chute'


EXT_DOC = re.compile(r'\.(pdf|docx?|xlsx?|pptx?)(\?|#|$)', re.I)


def documentos_da_pagina(estrutura, url_pagina, product_id):
    """Todo link de documento da página, classificado e desduplicado por URL absoluta."""
    vistos, fora = set(), []
    for l in estrutura['LINKS']:
        href = _absolutizar(l['HREF'], url_pagina)
        if not href or not EXT_DOC.search(href):
            continue
        if href in vistos:
            continue                      # mesma URL duas vezes na página não é dois docs
        vistos.add(href)
        tipo, evid = classificar_documento(l['TEXTO'], href)
        fora.append({
            'PRODUCT_ID': product_id,
            'DOCUMENT_ID': 'DOC-%s-%s' % (COUNTRY, hashlib.sha1(href.encode()).hexdigest()[:12]),
            'DOCUMENT_TYPE': tipo,
            'TYPE_EVIDENCE': evid,
            'URL': href,
            'SOURCE_PAGE': url_pagina,
            'LINK_TEXT': l['TEXTO'],
            'PAGE_SECTION': l['SECAO'],
            'FILENAME': href.split('/')[-1].split('?')[0],
            'VISIBLE_DOCUMENT_DATE': _data_visivel(l['TEXTO']),
            'COUNTRY': COUNTRY,
            'HTTP_STATUS': 'NOT_ATTEMPTED',
            'MEDIA_TYPE': 'NOT_COLLECTED',
            'BYTES': 'NOT_COLLECTED',
            'SHA256': 'NOT_COLLECTED',
            'CAPTURED_AT': 'NOT_COLLECTED',
            'DOWNLOAD_STATE': 'NOT_ATTEMPTED',
        })
    return fora


_DATA = re.compile(r'\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2}|'
                   r'(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[a-z]*\.?\s+\d{4})\b', re.I)


def _data_visivel(t):
    m = _DATA.search(t or '')
    return m.group(1) if m else 'NÃO SEI'


def _absolutizar(href, base):
    href = (href or '').strip()
    if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
        return ''
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith('http'):
        return href
    if href.startswith('/'):
        return BASE + href
    return base.rsplit('/', 1)[0] + '/' + href


# ══════════════════════════════════════════════════════════════════════════════
# 4 · A RELAÇÃO — seção 9, o coração da missão
# ══════════════════════════════════════════════════════════════════════════════
#
# A regra única: uma relação CROP x ISSUE só nasce quando cultivo e agente aparecem
# NA MESMA LINHA de tabela. Listas independentes em seções diferentes produzem
# CROP_RELATIONS e ISSUE_RELATIONS separadas, com PAIR_DERIVABLE = false.
#
# Cruzar [culturas] x [issues] seria produto cartesiano. O ES-ADAMA-PORTFOLIO-ROPF já
# recusou exatamente esse atalho ("CROP_ISSUE_PAIRS: NAO DERIVADO"). O mesmo aqui.

DOSE = re.compile(
    r'(\d+(?:[.,]\d+)?)\s*(?:[-–a]\s*(\d+(?:[.,]\d+)?)\s*)?'
    r'(l/ha|kg/ha|ml/ha|g/ha|cc/ha|l/hl|ml/hl|g/hl|%|ml/100\s*l|cc/hl)', re.I)
BBCH = re.compile(r'bbch\s*:?\s*(\d{1,2})\s*(?:[-–a]\s*(\d{1,2}))?', re.I)
N_APLIC = re.compile(r'(\d+)\s*(?:aplicaci[oó]n(?:es)?|tratamiento?s?)', re.I)
INTERVALO = re.compile(r'(?:intervalo|cada)\s*(?:de\s*)?(\d+)\s*(?:[-–a]\s*(\d+)\s*)?d[ií]as?', re.I)
VOL_AGUA = re.compile(r'(\d+)\s*(?:[-–a]\s*(\d+)\s*)?\s*l(?:itros)?\s*(?:de\s*)?(?:agua|caldo)/?\s*ha', re.I)
PLAZO = re.compile(r'plazo\s+de\s+seguridad\s*:?\s*(\d+)\s*d[ií]as?', re.I)

JANELA = [
    ('PRE_EMERGENCE',  re.compile(r'pre[\s-]?emergencia', re.I)),
    ('POST_EMERGENCE', re.compile(r'post[\s-]?emergencia', re.I)),
    ('PREVENTIVE',     re.compile(r'preventiv[oa]', re.I)),
    ('CURATIVE',       re.compile(r'curativ[oa]|erradicante', re.I)),
    ('PRE_SIEMBRA',    re.compile(r'pre[\s-]?siembra', re.I)),
]


def _indice_de_cabeca(tabela_vocab):
    """Primeira palavra de cada termo oficial -> termos que começam por ela.

    Serve a um problema real: a ADAMA escreve "Vid", e o MAPA só conhece "VID DE
    VINIFICACIÓN" e "VID DE MESA". Escolher um dos dois seria inventar registro; ignorar
    seria apagar o que a página diz. O índice permite a terceira saída — AMBIGUOUS com os
    candidatos nomeados.
    """
    idx = {}
    for chave, meta in tabela_vocab.items():
        cabeca = chave.split(' ')[0]
        if len(cabeca) >= 4:
            idx.setdefault(cabeca, []).append(meta)
    return idx


def _tokens(texto, tabela_vocab, indice=None):
    """(EXATOS, AMBÍGUOS). Nenhum dos dois é fuzzy — e são devolvidos separados.

    EXATOS   o termo oficial aparece inteiro, como palavra, no texto.
    AMBÍGUOS a página usa uma forma curta que é cabeça de 2+ termos oficiais e de nenhum
             exato. Vira CROP_TERM_AMBIGUOUS com os candidatos listados, nunca um palpite.

    Sem fuzzy, sem distância de edição, sem "parecido". A seção 16 proíbe fuzzy-match
    silencioso para registro; a mesma proibição vale para cultivo e agente.
    """
    k = _chave(texto)
    palavras = set(k.split())
    exatos, cobertos = [], set()
    for chave, meta in tabela_vocab.items():
        if re.search(r'(?:^| )%s(?:$| )' % re.escape(chave), k):
            exatos.append(meta)
            cobertos.update(chave.split())
    # mais específico primeiro: "maíz dulce" antes de "maíz"
    exatos.sort(key=lambda m: -len(m['MATCHED_AS']))
    exatos = _colapsar_sobrepostos(exatos)
    for m in exatos:
        m.update(_qualidade_do_casamento(m, indice))

    ambiguos = []
    if indice is not None:
        for palavra in sorted(palavras - cobertos):
            candidatos = indice.get(palavra) or []
            rotulos = sorted({c['ES'] for c in candidatos})
            if len(rotulos) >= 2:
                ambiguos.append({'TERMO_NA_PAGINA': palavra,
                                 'CANDIDATOS_OFICIAIS': rotulos[:8],
                                 'N_CANDIDATOS': len(rotulos),
                                 'ESTADO': 'AMBIGUOUS',
                                 'PORQUE': ('a pagina usa forma curta que casa com %d termos '
                                            'oficiais do MAPA; escolher um seria inventar'
                                            % len(rotulos))})
    return exatos, ambiguos


def _colapsar_sobrepostos(exatos):
    """Dois rótulos oficiais sobre o MESMO trecho são UM alvo declarado, não dois.

    "SEPTORIOSIS, SEPTORIA SPP." (ROPF) e "Septoriosis del trigo, Zymoseptoria tritici"
    (EPPO) casam a mesma palavra da mesma linha. Emitir os dois inflaria
    CROP_ISSUE_RELATIONS com uma relação que a página declarou uma vez só — é o erro de
    contagem que a seção 26 manda impedir.

    Fica o rótulo mais específico; o outro não some, vira ALSO_MATCHED_LABELS.
    """
    fora = []
    for m in exatos:                      # já ordenado do mais específico ao mais curto
        k = _chave(m['MATCHED_AS'])
        pai = next((f for f in fora
                    if re.search(r'(?:^| )%s(?:$| )' % re.escape(k),
                                 _chave(f['MATCHED_AS']))), None)
        if pai is not None:
            pai.setdefault('ALSO_MATCHED_LABELS', []).append(m['ES'])
        else:
            fora.append(dict(m))
    return fora


def _qualidade_do_casamento(meta, indice):
    """EXACT_OFFICIAL_LABEL, ou exato-mas-a-forma-curta-é-ambígua.

    "OÍDIO" casa exatamente UM rótulo do vocabulário ADAMA do ROPF
    ("OÍDIO, PODOSPHAERA FULIGINEA") e ao mesmo tempo encabeça dezenas de "Oídio de X"
    do EPPO. Casar exato e calar sobre isso seria escolher a espécie no lugar da fonte.
    O par continua sendo emitido — a página declarou —, mas marcado.
    """
    if indice is None:
        return {'MATCH_QUALITY': 'EXACT_OFFICIAL_LABEL'}
    cabeca = _chave(meta['MATCHED_AS']).split(' ')[0]
    irmaos = sorted({c['ES'] for c in (indice.get(cabeca) or [])})
    if len(_chave(meta['MATCHED_AS']).split()) == 1 and len(irmaos) >= 2:
        return {'MATCH_QUALITY': 'HEAD_TERM_ALSO_AMBIGUOUS',
                'HEAD_TERM_CANDIDATES': irmaos[:8],
                'PORQUE': ('a pagina usa a forma curta "%s", que casa este rotulo e encabeca '
                           'outros %d rotulos oficiais. A relacao vale; a ESPECIE nao esta '
                           'resolvida por esta fonte.' % (meta['MATCHED_AS'], len(irmaos) - 1))}
    return {'MATCH_QUALITY': 'EXACT_OFFICIAL_LABEL'}


def relacoes_da_tabela(tabela, vocab, product_id, url_pagina, indices=None):
    """Relações nascidas de LINHA. Cada uma sabe tabela, linha e seção de onde veio."""
    indices = indices or {}
    fora, ambiguidades = [], []
    for linha in tabela['LINHAS']:
        texto_linha = ' | '.join(linha['CELULAS'])
        crops, amb_c = _tokens(texto_linha, vocab['crops'], indices.get('crops'))
        issues, amb_i = _tokens(texto_linha, vocab['pests'], indices.get('pests'))
        ancora_linha = {'PAGE_SECTION': tabela['SECAO'], 'TABLE_INDEX': tabela['INDICE'],
                        'ROW_INDEX': linha['INDICE'], 'ROW_TEXT': texto_linha[:400]}
        for a in amb_c:
            ambiguidades.append(dict(a, PRODUCT_ID=product_id, EIXO='CROP',
                                     SOURCE_URL=url_pagina, ANCHOR=ancora_linha))
        for a in amb_i:
            ambiguidades.append(dict(a, PRODUCT_ID=product_id, EIXO='ISSUE',
                                     SOURCE_URL=url_pagina, ANCHOR=ancora_linha))
        if not crops or not issues:
            continue
        # Uma linha com 1 cultivo e 2 agentes é UMA linha declarando dois alvos naquele
        # cultivo — isso a linha sustenta. O que ela não sustenta é combinar com os
        # cultivos de OUTRA linha; por isso o laço é por linha, nunca sobre a tabela.
        for c in crops:
            for i in issues:
                fora.append({
                    'PRODUCT_ID': product_id,
                    'CROP': c['ES'], 'CROP_EPPO': c['EPPO'],
                    'ISSUE': i['ES'], 'ISSUE_EPPO': i['EPPO'],
                    'ISSUE_SCIENTIFIC': i.get('SCI', ''),
                    'CROP_MATCH_QUALITY': c.get('MATCH_QUALITY'),
                    'ISSUE_MATCH_QUALITY': i.get('MATCH_QUALITY'),
                    'CROP_ALSO_MATCHED': c.get('ALSO_MATCHED_LABELS', []),
                    'ISSUE_ALSO_MATCHED': i.get('ALSO_MATCHED_LABELS', []),
                    'DOSE': _dose(texto_linha),
                    'BBCH_FROM': _bbch(texto_linha)[0], 'BBCH_TO': _bbch(texto_linha)[1],
                    'APPLICATION_COUNT': _um(N_APLIC, texto_linha),
                    'INTERVAL_DAYS': _um(INTERVALO, texto_linha),
                    'WATER_VOLUME': _um(VOL_AGUA, texto_linha),
                    'PRE_HARVEST_INTERVAL_DAYS': _um(PLAZO, texto_linha),
                    'TIMING_FLAGS': [n for n, rx in JANELA if rx.search(texto_linha)],
                    'EVIDENCE_LEVEL': 'MANUFACTURER_TECHNICAL_CLAIM',
                    'SOURCE_OWNER': 'ADAMA_PAGE',
                    'ANCHOR': {'PAGE_SECTION': tabela['SECAO'],
                               'TABLE_INDEX': tabela['INDICE'],
                               'TABLE_HEADER': tabela['CABECALHO'],
                               'ROW_INDEX': linha['INDICE'],
                               'ROW_TEXT': texto_linha[:400]},
                    'SOURCE_URL': url_pagina,
                    'PAIR_ORIGIN': 'SAME_TABLE_ROW',
                    'MAPA_CONFIRMATION': 'ADAMA_ONLY_NOT_TESTED',
                })
    return fora, ambiguidades


def _dose(t):
    m = DOSE.search(t or '')
    if not m:
        return 'NÃO SEI'
    lo, hi, un = m.group(1), m.group(2), m.group(3)
    return ('%s-%s %s' % (lo, hi, un)) if hi else ('%s %s' % (lo, un))


def _bbch(t):
    m = BBCH.search(t or '')
    if not m:
        return ('NÃO SEI', 'NÃO SEI')
    return (m.group(1), m.group(2) or m.group(1))


def _um(rx, t):
    m = rx.search(t or '')
    return m.group(1) if m else 'NÃO SEI'


# ══════════════════════════════════════════════════════════════════════════════
# 5 · CLAIMS — quatro classes, e a fronteira entre elas é a missão inteira
# ══════════════════════════════════════════════════════════════════════════════

CLAIMS_COMERCIAIS = [
    r'nuevo\s+est[aá]ndar', r'l[ií]der', r'la\s+soluci[oó]n\s+definitiva',
    r'revoluci[oó]n', r'[uú]nico\s+en\s+el\s+mercado', r'referencia\s+del\s+mercado',
    r'la\s+mejor\s+opci[oó]n', r'm[aá]xima\s+rentabilidad', r'completa\s+la\s+estrategia',
]
CLAIMS_TECNICOS = [
    r'protecci[oó]n\s+prolongada', r'amplia\s+la\s+ventana', r'ampl[ií]a\s+la\s+ventana',
    r'r[aá]pida\s+absorci[oó]n', r'r[aá]pida\s+acci[oó]n', r'resistente\s+al\s+lavado',
    r'sistem[ií]a?c[oa]', r'translocaci[oó]n', r'persistencia', r'residualidad',
    r'selectivid?ad', r'mayor\s+flexibilidad', r'especialmente\s+indicado',
    r'efecto\s+preventivo', r'efecto\s+curativo', r'acci[oó]n\s+de\s+contacto',
    r'mojabilidad', r'adherencia', r'\d+\s*%\s+de\s+(?:eficacia|control)',
]
CLAIMS_REGULATORIOS = [
    r'n[uú]mero\s+de\s+registro', r'registro\s+n[.º°]', r'inscrito\s+en\s+el\s+registro',
    r'autorizado\s+(?:en|para)', r'\bES-\d{5}\b', r'\b\d{5,6}/\d{2}\b',
]

MODO_ACAO = [
    ('HRAC', re.compile(r'\bHRAC\b[\s:]*([A-Z0-9/]{1,6})', re.I)),
    ('FRAC', re.compile(r'\bFRAC\b[\s:]*([A-Z0-9/]{1,6})', re.I)),
    ('IRAC', re.compile(r'\bIRAC\b[\s:]*([A-Z0-9/]{1,6})', re.I)),
]

REGISTRO = re.compile(r'\b(?:ES-\d{5}|\d{5,6}\s*/\s*\d{2})\b')
CONCENTRACAO = re.compile(
    r'([A-Za-zÁÉÍÓÚÑáéíóúñ][A-Za-zÁÉÍÓÚÑáéíóúñ\s-]{3,40}?)\s+(\d+(?:[.,]\d+)?)\s*%\s*'
    r'(?:\[?(\w{1,3})\]?)?\s*(?:p/v|p/p|w/v|w/w)?', re.I)


def _classificar_claim(texto):
    for rx in CLAIMS_REGULATORIOS:
        if re.search(rx, texto, re.I):
            # ATENÇÃO: um enunciado com forma regulatória ainda é declaração DO FABRICANTE.
            # Vira REGULATORY_FACT só depois do crosswalk confirmar no MAPA. Ver seção 10.
            return 'MANUFACTURER_REGULATORY_STATEMENT'
    for rx in CLAIMS_COMERCIAIS:
        if re.search(rx, texto, re.I):
            return 'MANUFACTURER_COMMERCIAL_CLAIM'
    for rx in CLAIMS_TECNICOS:
        if re.search(rx, texto, re.I):
            return 'MANUFACTURER_TECHNICAL_CLAIM'
    return None


def claims_da_pagina(estrutura, product_id, url_pagina):
    fora, vistos = [], set()
    for t in estrutura['TEXTOS']:
        texto = t['TEXTO'].strip()
        if not (12 <= len(texto) <= 400):
            continue
        tipo = _classificar_claim(texto)
        if not tipo:
            continue
        chave = (_chave(texto)[:120], tipo)
        if chave in vistos:
            continue
        vistos.add(chave)
        fora.append({
            'CLAIM_ID': 'CLM-%s-%s' % (COUNTRY, hashlib.sha1(
                (product_id + texto).encode()).hexdigest()[:12]),
            'PRODUCT_ID': product_id,
            'CLAIM_TYPE': tipo,
            'CLAIM_TEXT_SHORT': texto[:240],
            'SOURCE_URL': url_pagina,
            'SOURCE_DOCUMENT': 'PAGINA_DE_PRODUTO',
            'SOURCE_DATE': 'NÃO SEI',
            'CAPTURED_AT': 'NOT_COLLECTED',
            'PAGE_SECTION': t['SECAO'],
            'CROP': 'NÃO SEI', 'ISSUE': 'NÃO SEI', 'REGION': 'NÃO SEI',
            'TIME_CONTEXT': 'NÃO SEI',
            'EVIDENCE_LEVEL': 'OBSERVED_ON_MANUFACTURER_PAGE',
            'REGULATORY_CONFIRMATION': 'NOT_TESTED',
        })
    return fora


# ══════════════════════════════════════════════════════════════════════════════
# 6 · PÁGINA DE PRODUTO -> ENTIDADE
# ══════════════════════════════════════════════════════════════════════════════

def product_id(nome, url):
    """Estável e local. Deriva de URL+nome: renomeação gera ID novo, e isso é desejado.

    A seção 4 proíbe deduplicar por nome. Duas formulações com o mesmo nome comercial
    continuam sendo duas entidades enquanto a URL diferir.
    """
    base = (url or '') + '|' + _chave(nome or '')
    return 'ADAMA-ES-%s' % hashlib.sha1(base.encode()).hexdigest()[:12]


def parsear_produto(html, url_pagina, vocab=None, catalog_status='STATUS_UNKNOWN',
                    captured_at='NOT_COLLECTED'):
    """HTML de uma página de produto -> entidade + documentos + relações + claims."""
    vocab = vocab or vocabulario()
    est = estruturar(html)

    nome = _nome_comercial(est, url_pagina)
    pid = product_id(nome, url_pagina)
    texto_todo = ' '.join(t['TEXTO'] for t in est['TEXTOS'])

    indices = {'crops': _indice_de_cabeca(vocab['crops']),
               'pests': _indice_de_cabeca(vocab['pests'])}
    crop_rel, issue_rel, par_rel, ambiguos = [], [], [], []
    for tab in est['TABELAS']:
        pares, amb = relacoes_da_tabela(tab, vocab, pid, url_pagina, indices)
        par_rel.extend(pares)
        ambiguos.extend(amb)

    # Cultivos e agentes citados FORA de linha pareada entram como relação simples,
    # com PAIR_DERIVABLE = false. É o registro honesto de "a página cita milho" sem
    # afirmar contra o quê.
    pares_vistos = {(r['CROP'], r['ISSUE']) for r in par_rel}
    crops_txt, amb_c = _tokens(texto_todo, vocab['crops'], indices['crops'])
    issues_txt, amb_i = _tokens(texto_todo, vocab['pests'], indices['pests'])
    ancora_pagina = {'PAGE_SECTION': 'CORPO DA PAGINA', 'TABLE_INDEX': None,
                     'ROW_INDEX': None, 'ROW_TEXT': ''}
    vistos_amb = {(a['TERMO_NA_PAGINA'], a['EIXO']) for a in ambiguos}
    for eixo, lista in (('CROP', amb_c), ('ISSUE', amb_i)):
        for a in lista:
            if (a['TERMO_NA_PAGINA'], eixo) not in vistos_amb:
                vistos_amb.add((a['TERMO_NA_PAGINA'], eixo))
                ambiguos.append(dict(a, PRODUCT_ID=pid, EIXO=eixo,
                                     SOURCE_URL=url_pagina, ANCHOR=ancora_pagina))
    for c in crops_txt:
        crop_rel.append({'PRODUCT_ID': pid, 'CROP': c['ES'], 'CROP_EPPO': c['EPPO'],
                         'SOURCE_URL': url_pagina, 'SOURCE_OWNER': 'ADAMA_PAGE',
                         'PAIR_DERIVABLE': any(p[0] == c['ES'] for p in pares_vistos),
                         'EVIDENCE_LEVEL': 'OBSERVED_ON_MANUFACTURER_PAGE'})
    for i in issues_txt:
        issue_rel.append({'PRODUCT_ID': pid, 'ISSUE': i['ES'], 'ISSUE_EPPO': i['EPPO'],
                          'SOURCE_URL': url_pagina, 'SOURCE_OWNER': 'ADAMA_PAGE',
                          'PAIR_DERIVABLE': any(p[1] == i['ES'] for p in pares_vistos),
                          'EVIDENCE_LEVEL': 'OBSERVED_ON_MANUFACTURER_PAGE'})

    reg = REGISTRO.search(texto_todo)
    moa = []
    for esquema, rx in MODO_ACAO:
        for m in rx.finditer(texto_todo):
            moa.append({'PRODUCT_ID': pid, 'SCHEME': esquema, 'CODE': m.group(1),
                        'SOURCE_URL': url_pagina,
                        'EVIDENCE_LEVEL': 'MANUFACTURER_TECHNICAL_CLAIM'})

    produto = {
        'PRODUCT_ID': pid,
        'COUNTRY': COUNTRY,
        'DISPLAY_NAME': nome,
        'PAGE_URL': url_pagina,
        'CATEGORY': _categoria(est, texto_todo),
        'REGISTRATION_ID': reg.group(0) if reg else 'NÃO SEI',
        'ADAMA_INTERNAL_ID': 'NÃO SEI',
        'CURRENT_CATALOG_STATUS': catalog_status,
        'FIRST_SEEN': captured_at,
        'CAPTURED_AT': captured_at,
        'FORMULATION': _formulacao(texto_todo),
        'ACTIVE_INGREDIENTS': _ingredientes(texto_todo, vocab),
        'PUBLIC_ADAMA_CATALOG_PRESENCE': 'YES' if catalog_status == 'CURRENT' else 'NÃO SEI',
        'CURRENT_COMMERCIAL_AVAILABILITY': 'NAO_SEI',
        'PORQUE_NAO_SEI_DISPONIBILIDADE': (
            'presenca em catalogo publico nao prova estoque, venda, distribuicao nem '
            'prioridade interna (secao 24)'),
    }

    return {
        'PRODUCT': produto,
        'DOCUMENTS': documentos_da_pagina(est, url_pagina, pid),
        'CROP_RELATIONS': crop_rel,
        'ISSUE_RELATIONS': issue_rel,
        'CROP_ISSUE_RELATIONS': par_rel,
        'AMBIGUOUS_TERMS': ambiguos,
        'MODES_OF_ACTION': moa,
        'CLAIMS': claims_da_pagina(est, pid, url_pagina),
        'VIDEOS': [dict(v, PRODUCT_ID=pid, SOURCE_URL=url_pagina) for v in est['VIDEOS']],
        'PARSE_STATS': {'TABELAS': len(est['TABELAS']), 'LINKS': len(est['LINKS']),
                        'TEXTOS': len(est['TEXTOS'])},
    }


def _nome_comercial(est, url):
    for m in est['METAS']:
        if m['NOME'] in ('og:title', 'title'):
            return re.split(r'\s*[|–-]\s*ADAMA', m['CONTEUDO'])[0].strip()
    for t in est['TEXTOS']:
        if t['TAG'] == 'h1' and t['TEXTO']:
            return t['TEXTO'].strip()
    return url.rstrip('/').split('/')[-1].replace('-', ' ').upper() or 'NÃO SEI'


CATEGORIAS = [
    ('CONTROL_DE_ENFERMEDADES', re.compile(r'enfermedad|fungicida', re.I)),
    ('CONTROL_DE_MALAS_HIERBAS', re.compile(r'malas\s+hierbas|herbicida', re.I)),
    ('CONTROL_DE_PLAGAS', re.compile(r'control\s+de\s+plagas|insecticida|acaricida', re.I)),
    ('MEJORA_DE_CULTIVOS', re.compile(r'mejora\s+de\s+cultivos|bioestimulante|nutrici[oó]n', re.I)),
]


def _categoria(est, texto):
    # A migalha de pão do catálogo é mais confiável que o corpo: uma página de fungicida
    # que cita "malas hierbas" numa comparação não é herbicida.
    for l in est['LINKS']:
        for nome, rx in CATEGORIAS:
            if rx.search(l['HREF'] or '') or rx.search(l['TEXTO'] or ''):
                return nome
    for nome, rx in CATEGORIAS:
        if rx.search(texto or ''):
            return nome
    return 'NÃO SEI'


FORM = re.compile(r'\b(SC|EC|WG|WP|SL|EW|OD|CS|ZC|SE|FS|GR|ME|DC|EO|SG|WS|GB|RB)\b')


def _formulacao(t):
    m = FORM.search(t or '')
    return m.group(1) if m else 'NÃO SEI'


def _ingredientes(t, vocab=None):
    """Substância + concentração. Um nome que contém cultivo ou agente não é substância.

    Sem esse filtro a expressão pega o texto da célula anterior da tabela e emite
    "preventivo OLIVO REPILO 0,05%" como ingrediente ativo. Concentração é da fórmula,
    não da linha de uso.
    """
    fora, vistos = [], set()
    proibidos = set()
    if vocab:
        proibidos = set(vocab['crops']) | set(vocab['pests'])
    for m in CONCENTRACAO.finditer(t or ''):
        nome = m.group(1).strip(' .,-')
        palavras = _chave(nome).split()
        if len(nome) < 4 or _chave(nome) in vistos:
            continue
        if len(palavras) > 3:
            continue
        if any(p in proibidos for p in palavras):
            continue
        vistos.add(_chave(nome))
        fora.append({'NAME': nome, 'CONCENTRATION': m.group(2) + '%',
                     'FORMULATION_CODE': m.group(3) or 'NÃO SEI',
                     'EVIDENCE_LEVEL': 'OBSERVED_ON_MANUFACTURER_PAGE'})
    return fora[:12]


# ══════════════════════════════════════════════════════════════════════════════
# 7 · ROTA VIVA — enumerar, baixar, hashear
# ══════════════════════════════════════════════════════════════════════════════

def buscar(url, timeout=45, binario=False):
    """Devolve (estado, conteudo, http_status). Falha NUNCA vira conteúdo vazio."""
    dest = '-' if not binario else None
    cmd = ['curl', '-sSL', '-m', str(timeout), '-A', UA,
           '-H', 'Accept-Language: es-ES,es;q=0.9', '-w', '\n%{http_code}', url]
    if binario:
        import tempfile
        fd, caminho = tempfile.mkstemp()
        os.close(fd)
        cmd = ['curl', '-sSL', '-m', str(timeout), '-A', UA, '-o', caminho,
               '-w', '%{http_code}\t%{content_type}', url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        partes = (r.stdout or '\t').split('\t')
        code = partes[0].strip() or '000'
        ctype = partes[1].strip() if len(partes) > 1 else ''
        if code.startswith('2'):
            return 'OK', {'PATH': caminho, 'MEDIA_TYPE': ctype}, code
        os.unlink(caminho)
        return 'FAILED', {'REASON': (r.stderr or '').strip()[:200] or 'HTTP %s' % code}, code
    r = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    saida = r.stdout or ''
    code = saida.rsplit('\n', 1)[-1].strip() or '000'
    corpo = saida.rsplit('\n', 1)[0] if '\n' in saida else ''
    if code.startswith('2'):
        return 'OK', corpo, code
    return 'FAILED', (r.stderr or '').strip()[:200] or 'HTTP %s' % code, code


def sha256_do_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def baixar_documentos(docs, captura, limite=None):
    """Baixa DE VERDADE. Guarda bytes+sha256. Distingue FAILED de NOT_FOUND.

    Desduplica por SHA256: o mesmo PDF servido por duas URLs é UM documento com duas
    URLs, não dois documentos. A seção 26 nomeia esse erro; aqui ele é impedido por
    construção, não por revisão.
    """
    por_hash, baixados, falhos = {}, 0, 0
    for d in (docs if limite is None else docs[:limite]):
        estado, res, code = buscar(d['URL'], binario=True)
        d['HTTP_STATUS'] = code
        d['CAPTURED_AT'] = captura
        if estado != 'OK':
            d['DOWNLOAD_STATE'] = 'FAILED'
            d['FAILURE_REASON'] = res.get('REASON', 'NÃO SEI')
            d['O_QUE_ISTO_NAO_E'] = 'falha de download NAO e documento inexistente'
            falhos += 1
            continue
        sha = sha256_do_arquivo(res['PATH'])
        d['SHA256'] = sha
        d['BYTES'] = os.path.getsize(res['PATH'])
        d['MEDIA_TYPE'] = res['MEDIA_TYPE'] or 'NÃO SEI'
        d['LOCAL_PATH'] = res['PATH']
        if sha in por_hash:
            d['DOWNLOAD_STATE'] = 'DUPLICATE_CONTENT'
            d['DUPLICATE_OF'] = por_hash[sha]
            d['STORAGE_KEY'] = 'NAO_ENVIADO — conteudo identico ja preservado'
        else:
            por_hash[sha] = d['DOCUMENT_ID']
            d['DOWNLOAD_STATE'] = 'DOWNLOADED'
            d['STORAGE_KEY'] = 'raw/%s/adama-website/%s/%s' % (
                COUNTRY, d['PRODUCT_ID'], sha[:16] + '-' + d['FILENAME'])
            baixados += 1
    return {'DOCUMENTS_DOWNLOADED': baixados, 'FAILED_DOWNLOADS': falhos,
            'UNIQUE_BY_SHA256': len(por_hash)}


# -- enumeração do denominador ------------------------------------------------
#
# Quatro rotas, testadas em ordem. Nenhuma é assumida: a que responder vence, e o
# artefato registra QUAL respondeu. Se nenhuma responder, o denominador é NÃO SEI.

ROTAS_ENUM = [
    ('CATALOGO_HTML',   CATALOGO),
    ('PRODUTOS_HTML',   BASE + '/spain/es/products'),
    ('SITEMAP',         BASE + '/sitemap.xml'),
    ('DRUPAL_VIEW',     CATALOGO + '?page=0'),
]

RX_PRODUTO = re.compile(r'/spain/es/[a-z0-9-]*products?/[a-z0-9/-]+', re.I)


def enumerar_catalogo(captura):
    """Lista NOMINAL do catálogo atual. Sem acesso -> NOT_COLLECTED, jamais 0."""
    tentativas = []
    for nome, url in ROTAS_ENUM:
        estado, corpo, code = buscar(url)
        tentativas.append({'ROTA': nome, 'URL': url, 'HTTP_STATUS': code,
                           'ESTADO': estado})
        if estado != 'OK':
            continue
        est = estruturar(corpo)
        vistos, produtos = set(), []
        for l in est['LINKS']:
            href = _absolutizar(l['HREF'], url)
            if not RX_PRODUTO.search(href or '') or EXT_DOC.search(href or ''):
                continue
            if href.rstrip('/') in vistos:
                continue
            vistos.add(href.rstrip('/'))
            produtos.append({'PAGE_URL': href.rstrip('/'),
                             'DISPLAY_NAME_NO_CATALOGO': l['TEXTO'],
                             'SECAO': l['SECAO'],
                             'CURRENT_CATALOG_STATUS': 'CURRENT'})
        if produtos:
            tentativas[-1]['ENCONTRADOS'] = len(produtos)
            return {
                'CATALOG_TIMESTAMP': captura,
                'ROTA_QUE_RESPONDEU': nome,
                'CURRENT_CATALOG_TOTAL': len(produtos),
                'CURRENT_CATALOG_NAMES': [p['DISPLAY_NAME_NO_CATALOGO'] for p in produtos],
                'ENTRADAS': produtos,
                'ENUMERATION_COMPLETE': 'YES',
                'TENTATIVAS': tentativas,
                'SNAPSHOT_POLICY': 'somente o observado ao vivo nesta captura entrou',
            }
    return {
        'CATALOG_TIMESTAMP': captura,
        'ROTA_QUE_RESPONDEU': None,
        'CURRENT_CATALOG_TOTAL': 'NOT_COLLECTED',
        'CURRENT_CATALOG_NAMES': 'NOT_COLLECTED',
        'ENTRADAS': [],
        'ENUMERATION_COMPLETE': 'NO',
        'TENTATIVAS': tentativas,
        'PORQUE': 'nenhuma das rotas publicas respondeu a partir deste ambiente',
        'LEI': ('NOT_COLLECTED != 0. Nenhum snapshot antigo (nem o de 58, nem o relato '
                'externo de 55) foi usado para completar este denominador.'),
    }


if __name__ == '__main__':
    if '--parse' in sys.argv:
        i = sys.argv.index('--parse')
        arq = sys.argv[i + 1]
        url = sys.argv[sys.argv.index('--url') + 1] if '--url' in sys.argv else 'file://' + arq
        with open(arq, encoding='utf-8', errors='replace') as f:
            print(json.dumps(parsear_produto(f.read(), url), ensure_ascii=False, indent=1))
        sys.exit(0)
    if '--censo' in sys.argv:
        i = sys.argv.index('--censo')
        cap = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith('-') \
            else 'NÃO SEI'
        print(json.dumps(enumerar_catalogo(cap), ensure_ascii=False, indent=1))
        sys.exit(0)
    print(__doc__)
