#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PARSER CANÓNICO DO RÓTULO OFICIAL ITALIANO (T4) → LINHAS DE USO.

    python3 coleta/rotulo_t4_it.py ROTULO.pdf|.html|.txt --registo 004701 \
        [--csv data/samples/IT-SOURCE-SAMPLES/IT-T4-001/PROD_FTS_6_20260907.csv] \
        [--product-id IT-PRD-003] [--url URL_DE_ORIGEM]

Lê um documento JÁ GUARDADO (PDF/HTML/texto do EtichettaServlet do Ministero
della Salute) e a linha do registo oficial (CSV `PROD_FTS_6`, fonte IT-T4-001).
Nunca vai à rede: quem busca é `rotulos_baixar.py`; quem lê é este ficheiro.

A PERGUNTA QUE ELE RESPONDE
----------------------------
Para este produto, nesta cultura, contra este alvo: que dose, que época, que
restrição, e em que versão do documento? (CAP-LABEL / CAP-PORT, Bíblia § 34.)

Cada linha de uso sai com:

    PRODUCT_ID · NUMERO_REGISTO · TITULAR · PRINCIPIOS_ATIVOS · FORMULACAO
    DOCUMENTO (sha256 + data do decreto + validade do rótulo)
    CULTURA · ALVO · DOSE · EPOCA · RESTRICOES · INTERVALO_SEGURANCA
    VALIDADE_DA_AUTORIZACAO

e cada campo carrega o SEU estado, porque cada um tem prova diferente.

OS QUATRO ESTADOS — FECHADOS
-----------------------------
    VERIFICADO     duas fontes independentes dizem o mesmo (o registo oficial
                   e a letra do rótulo), ou o campo vem do registo oficial e o
                   rótulo foi reconhecido como deste registo
    ENCONTRADO     está escrito no documento, citado, mas ninguém o conferiu
    NAO_CONHECIDO  não achámos. NÃO quer dizer que não existe
    ERRO           o documento não abriu, ou as duas fontes contradizem-se

    NAO_PROVADO  ≠  NAO_AUTORIZADO

Um rótulo sem linha lida sai com `NAO_CONHECIDO` e com a afirmação proibida
escrita: «o produto não está autorizado para X» NUNCA nasce daqui. Este ficheiro
não tem, e não pode ter, o estado NAO_AUTORIZADO.

    APROVACAO_UE_DA_SUBSTANCIA  ≠  AUTORIZACAO_NACIONAL_DO_PRODUTO

A substância aprovada em Bruxelas não autoriza o produto em Itália, e a
substância sem ato europeu encontrado não desautoriza nada. As duas vivem em
campos separados e nenhuma escreve na outra.

A LEI DO PAR (herdada de `rotulos_ler.py`)
-------------------------------------------
Cultura e alvo só se unem DENTRO de uma linha da tabela (ou do bloco que a
cultura encabeça). Nunca se cruza tudo com tudo. Dose, época e restrição também
são da linha: o que está noutra linha não vem para esta.
"""
import csv
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rotulos_ler as RL  # noqa: E402 — cultura, alvo e desenho da tabela: um dono só

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_REGISTO = os.path.join(ROOT, 'data', 'samples', 'IT-SOURCE-SAMPLES',
                           'IT-T4-001', 'PROD_FTS_6_20260907.csv')
EU_ATOS = os.path.join(ROOT, 'data', 'samples', 'EU-T4-001',
                       'sparql-active-substance-2026.json')

SCHEMA = 'sintonia.rotulo-t4-it/1'
SOURCE_ID_REGISTO = 'IT-T4-001'

VERIFICADO = 'VERIFICADO'
ENCONTRADO = 'ENCONTRADO'
NAO_CONHECIDO = 'NAO_CONHECIDO'
ERRO = 'ERRO'
ESTADOS = (VERIFICADO, ENCONTRADO, NAO_CONHECIDO, ERRO)

AFIRMACAO_PROIBIDA = ('a ausencia de linha lida NAO prova que o produto nao esta '
                      'autorizado. NAO_PROVADO != NAO_AUTORIZADO.')


def campo(valor, estado, fonte, citacao=None):
    """Um campo = valor + estado + de onde veio. Nunca um valor solto."""
    if estado not in ESTADOS:
        raise ValueError('estado fora do vocabulario fechado: %r' % estado)
    if estado == NAO_CONHECIDO:
        valor = None
    c = {'VALOR': valor, 'ESTADO': estado, 'FONTE': fonte}
    if citacao:
        c['CITACAO'] = citacao
    return c


def _n(t):
    return ''.join(ch for ch in unicodedata.normalize('NFD', t or '')
                   if unicodedata.category(ch) != 'Mn').lower()


def _num_registo(txt):
    """«15253», «015253», «n. 15.253» → '015253'. O registo tem 6 dígitos."""
    d = re.sub(r'\D', '', txt or '')
    return d.zfill(6) if d else None


# ══════════════════════════════════════════════════════════════════════════════
# 1. O REGISTO OFICIAL (IT-T4-001, CSV PROD_FTS_6)
# ══════════════════════════════════════════════════════════════════════════════
# stato_amministrativo é vocabulário do Ministero. Medido no snapshot 20260907:
# Autorizzato*, Ri-registrato*, Rinnovato* = vivo; Revocato, Scaduto, Sospeso = não.
VIVO = re.compile(r'^(autorizzato|ri-registrato|rinnovato)', re.I)


def ler_registo(caminho=CSV_REGISTO):
    """→ {numero: linha_do_csv}. O CSV é a fonte; aqui não se corrige nada."""
    with open(caminho, encoding='utf-8', newline='') as f:
        return {r['num_registrazione']: r for r in csv.DictReader(f, delimiter=';')}


def _data_it(txt):
    """'31/10/2026' → '2026-10-31'. '-' ou vazio → None."""
    m = re.match(r'^\s*(\d{1,2})[/.](\d{1,2})[/.](\d{4})\s*$', txt or '')
    return '%s-%02d-%02d' % (m.group(3), int(m.group(2)), int(m.group(1))) if m else None


def ficha_do_registo(registo, numero, snapshot='PROD_FTS_6'):
    """→ ficha do produto segundo o registo. Sem linha → tudo NAO_CONHECIDO."""
    num = _num_registo(numero)
    r = registo.get(num) if num else None
    fonte = '%s · %s' % (SOURCE_ID_REGISTO, snapshot)
    if r is None:
        nc = campo(None, NAO_CONHECIDO, fonte)
        return {'NUMERO_REGISTO': campo(num, ENCONTRADO, 'pedido') if num else nc,
                'NO_REGISTO': False, 'PRODUTO': nc, 'TITULAR': nc,
                'PRINCIPIOS_ATIVOS': nc, 'FORMULACAO': nc, 'ATIVIDADE': nc,
                'ESTADO_ADMINISTRATIVO': nc, 'VALIDADE_DA_AUTORIZACAO': nc,
                'AUTORIZACAO_NACIONAL_VIVA': nc}
    sa = [s.strip() for s in re.split(r'\|', r['sostanze_attive']) if s.strip() not in ('', '-')]
    teor = [s.strip() for s in r['contenuto_per_100g_di_prodotto'].split('|')]
    estado_adm = r['stato_amministrativo'].strip()
    scad = _data_it(r['data_scadenza_autorizzazione'])
    return {
        'NUMERO_REGISTO': campo(num, ENCONTRADO, fonte),
        'NO_REGISTO': True,
        'PRODUTO': campo(r['denominazione_prodotto'].strip(), ENCONTRADO, fonte),
        'TITULAR': campo(r['ragione_sociale'].strip(), ENCONTRADO, fonte),
        'PRINCIPIOS_ATIVOS': campo(
            [{'SUBSTANCIA': s, 'TEOR_POR_100G': (teor[i] if i < len(teor) and teor[i] != '-' else None)}
             for i, s in enumerate(sa)] or None,
            ENCONTRADO if sa else NAO_CONHECIDO, fonte),
        'FORMULACAO': campo({'CODIGO': r['codice_formulazione'].strip(),
                             'DESCRICAO': r['descrizione_formulazione'].strip()},
                            ENCONTRADO, fonte),
        'ATIVIDADE': campo(r['attivita'].strip(), ENCONTRADO, fonte),
        'ESTADO_ADMINISTRATIVO': campo(estado_adm, ENCONTRADO, fonte),
        'VALIDADE_DA_AUTORIZACAO': campo(
            {'REGISTADO_EM': _data_it(r['data_registrazione']), 'EXPIRA_EM': scad},
            ENCONTRADO if scad else NAO_CONHECIDO, fonte),
        # vivo = o que o Ministero escreveu, lido na letra. Não se deduz da data.
        'AUTORIZACAO_NACIONAL_VIVA': campo(bool(VIVO.match(estado_adm)), ENCONTRADO, fonte),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2. O DOCUMENTO → TEXTO (sem rede, sem adivinhar)
# ══════════════════════════════════════════════════════════════════════════════
def _tipo(dados):
    if dados[:5] == b'%PDF-':
        return 'PDF'
    cab = dados[:2048].lstrip().lower()
    if cab.startswith(b'<!doctype html') or b'<html' in cab or b'<body' in cab:
        return 'HTML'
    return 'TEXTO'


def _pdf_para_texto(dados):
    """pypdf primeiro; `pdftotext` (sem -layout) se ele faltar ou falhar.

    Porque NÃO o -layout, medido nos 163 rótulos reais em 26/09: no -layout a
    célula centrada na vertical põe o alvo UMA LINHA ACIMA da cultura, e a regra
    «a linha começa na cultura» (rotulos_ler.py, afinada no texto do pypdf) cola o
    alvo à cultura de cima. Ler colunas pede geometria (-bbox-layout), não isto.

    Se os dois faltarem, o estado é ERRO com o nome da dependência — não se
    contorna com outra leitura inventada.
    """
    motivos = []
    try:
        import io
        import pypdf
        leitor = pypdf.PdfReader(io.BytesIO(dados))
        texto = '\n'.join((pg.extract_text() or '') for pg in leitor.pages)
        if texto.strip():
            return texto, 'pypdf'
        motivos.append('pypdf: sem texto')
    except ImportError:
        motivos.append('pypdf: DEPENDENCIA_EM_FALTA')
    except Exception as e:  # PDF que o pypdf não abre: tenta o poppler antes de ERRO
        motivos.append('pypdf: %s' % type(e).__name__)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'r.pdf')
        with open(p, 'wb') as f:
            f.write(dados)
        try:
            out = subprocess.run(['pdftotext', '-enc', 'UTF-8', p, '-'],
                                 capture_output=True, timeout=120)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.decode('utf-8', 'replace'), 'pdftotext'
            motivos.append('pdftotext: rc=%d' % out.returncode)
        except (OSError, subprocess.TimeoutExpired) as e:
            motivos.append('pdftotext: DEPENDENCIA_EM_FALTA' if isinstance(e, OSError)
                           else 'pdftotext: timeout')
    raise RuntimeError('; '.join(motivos))


class _SoTexto(__import__('html.parser').parser.HTMLParser):
    BLOCO = {'p', 'div', 'br', 'tr', 'li', 'h1', 'h2', 'h3', 'h4', 'table', 'section'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes, self._salta = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self._salta += 1
        elif tag in self.BLOCO:
            self.partes.append('\n')
        elif tag in ('td', 'th'):
            self.partes.append('   ')   # célula = coluna, como no -layout

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self._salta:
            self._salta -= 1
        elif tag in self.BLOCO:
            self.partes.append('\n')

    def handle_data(self, data):
        if not self._salta:
            self.partes.append(data)


def texto_do_documento(dados):
    """→ (texto, documento). `documento` diz o que foi lido e o hash dos bytes."""
    doc = {'SHA256': hashlib.sha256(dados or b'').hexdigest(),
           'BYTES': len(dados or b''), 'TIPO': None, 'EXTRATOR': None,
           'ESTADO': None, 'MOTIVO': None}
    if not dados:
        doc.update(ESTADO=ERRO, MOTIVO='documento vazio (0 bytes)')
        return '', doc
    tipo = _tipo(dados)
    doc['TIPO'] = tipo
    try:
        if tipo == 'PDF':
            texto, ext = _pdf_para_texto(dados)
        elif tipo == 'HTML':
            p = _SoTexto()
            p.feed(dados.decode('utf-8', 'replace'))
            texto, ext = html.unescape(''.join(p.partes)), 'html.parser'
        else:
            texto, ext = dados.decode('utf-8', 'replace'), 'utf-8'
    except Exception as e:  # o erro vira estado declarado, nunca silêncio
        doc.update(ESTADO=ERRO, MOTIVO='%s: %s' % (type(e).__name__, e))
        return '', doc
    texto = texto.replace('\x00', ' ').replace('\r\n', '\n').replace('\r', '\n')
    doc['EXTRATOR'] = ext
    if len(re.sub(r'\s', '', texto)) < 40:
        # PDF de imagem, ou a casca de HTML no lugar do PDF: não há letra para ler.
        doc.update(ESTADO=ERRO, MOTIVO='sem texto extraivel (%d caracteres)' % len(texto.strip()))
        return texto, doc
    doc['ESTADO'] = ENCONTRADO
    return texto, doc


# ══════════════════════════════════════════════════════════════════════════════
# 3. O CABEÇALHO DO RÓTULO (o que o próprio documento diz de si)
# ══════════════════════════════════════════════════════════════════════════════
MESES = {'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4, 'maggio': 5,
         'giugno': 6, 'luglio': 7, 'agosto': 8, 'settembre': 9, 'ottobre': 10,
         'novembre': 11, 'dicembre': 12}
_DATA = r'(\d{1,2}[./-]\d{1,2}[./-]\d{4}|\d{1,2}\s+(?:%s)\s+\d{4})' % '|'.join(MESES)

# Medido nos 163 rótulos: o número vem como «Registrazione Ministero della Salute
# n.», «Autorizzazione (del) Ministero della Salute n.», «Registrazione n° … del
# Ministero» e «Ministero della Sanità» nos antigos. Número solto («n. 1234 del»)
# sem a palavra do Ministero NÃO conta: pode ser o número de outro decreto.
_N = r'(?:n\.?|n°|nr\.?|numero)\s*(\d[\d.]{2,8})'
RX_REG_ROTULO = re.compile(
    r'(?:registrazione|autorizzazione)\s+(?:del\s+)?ministero\s+della\s+(?:salute|sanit[aà])\s*' + _N +
    r'|(?:registrazione|autorizzazione)\s+' + _N + r'[^\n]{0,40}?ministero', re.I)
RX_DECRETO = re.compile(r'etichetta\s+autorizzata\s+con\s+decreto\s+dirigenziale\s+del\s+' + _DATA, re.I)
RX_VALIDA = re.compile(r'valid(?:a|ità|ita)\s+(?:a\s+partire\s+)?da(?:l)?\s+' + _DATA +
                       r'(?:\s+al\s+' + _DATA + r')?', re.I)
RX_TITULAR = re.compile(r'titolare\s+(?:dell[a\'’]\s*)?(?:autorizzazione|registrazione)\s*[:.]?\s*([^\n]{3,120})', re.I)
RX_COMPOSICAO = re.compile(r'composizione\s*[:.]?\s*([^\n]{5,200})', re.I)


def _data_iso(txt):
    txt = (txt or '').strip().lower()
    m = re.match(r'^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$', txt)
    if m:
        return '%s-%02d-%02d' % (m.group(3), int(m.group(2)), int(m.group(1)))
    m = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})$', txt)
    if m and m.group(2) in MESES:
        return '%s-%02d-%02d' % (m.group(3), MESES[m.group(2)], int(m.group(1)))
    return None


def cabecalho_do_rotulo(texto):
    """→ campos que o rótulo declara sobre si mesmo. Cada um ENCONTRADO ou NAO_CONHECIDO."""
    plano = re.sub(r'[ \t]+', ' ', texto or '')
    f = 'rotulo'
    out = {}
    m = RX_REG_ROTULO.search(plano)
    out['NUMERO_REGISTO_NO_ROTULO'] = (campo(_num_registo(m.group(1) or m.group(2)), ENCONTRADO, f, m.group(0))
                                       if m else campo(None, NAO_CONHECIDO, f))
    m = RX_DECRETO.search(plano)
    out['DATA_DO_DECRETO'] = (campo(_data_iso(m.group(1)), ENCONTRADO, f, m.group(0))
                              if m and _data_iso(m.group(1)) else campo(None, NAO_CONHECIDO, f))
    m = RX_VALIDA.search(plano)
    if m and _data_iso(m.group(1)):
        out['VALIDADE_DO_ROTULO'] = campo({'DE': _data_iso(m.group(1)),
                                           'ATE': _data_iso(m.group(2)) if m.group(2) else None},
                                          ENCONTRADO, f, m.group(0))
    else:
        out['VALIDADE_DO_ROTULO'] = campo(None, NAO_CONHECIDO, f)
    m = RX_TITULAR.search(plano)
    out['TITULAR_NO_ROTULO'] = (campo(m.group(1).strip(' .;:'), ENCONTRADO, f, m.group(0).strip())
                                if m else campo(None, NAO_CONHECIDO, f))
    m = RX_COMPOSICAO.search(plano)
    out['COMPOSICAO_NO_ROTULO'] = (campo(re.sub(r'\s+', ' ', m.group(1)).strip(), ENCONTRADO, f)
                                   if m else campo(None, NAO_CONHECIDO, f))
    # o intervalo de segurança escrito FORA da tabela vale para o documento e fica
    # aqui — nunca é colado na última linha da tabela (lei do par)
    m = RX_PHI.search(plano)
    out['INTERVALO_DE_SEGURANCA_DO_DOCUMENTO'] = (
        campo({'DIAS': int(m.group(1)), 'ANTES_DE': m.group(2)}, ENCONTRADO, f, m.group(0).strip())
        if m else campo(None, NAO_CONHECIDO, f))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 4. CAMPOS DA LINHA: dose · época · restrições · intervalo de segurança
# ══════════════════════════════════════════════════════════════════════════════
# Unidade de dose como o rótulo escreve. A ordem importa: «g/100 l» antes de «g».
_UNID = (r'(?:m[lL]|[lL]|kg|Kg|KG|g|G)(?:\s*(?:di\s+)?(?:p\.?\s*f\.?|pf|prodotto\s+formulato|formulato))?'
         r'\s*/\s*(?:100\s*(?:l|lt|litri)\b|hl\b|ha\b|1000\s*m[q2²]|10\s*m[q2²]|m[q2²]\b)')
RX_DOSE = re.compile(
    r'(?<![\d/])(\d+(?:[.,]\d+)?)(?:\s*[-–÷]\s*(\d+(?:[.,]\d+)?))?\s*(' + _UNID + r')', re.I)
RX_UNIDADE = re.compile(_UNID, re.I)
# «numero» sem unidade na linha: a unidade vem do cabeçalho da coluna
RX_FAIXA = re.compile(r'(?<![\d/,.])(\d+(?:[.,]\d+)?)(?:\s*[-–÷]\s*(\d+(?:[.,]\d+)?))?(?![\d/])')

RX_MAX_TRAT = re.compile(
    r'(?:max(?:imo)?\.?\s*(?:n\.?\s*)?|non\s+(?:pi[uù]\s+di|oltre)\s+|fino\s+a\s+)(\d{1,2})\s*'
    r'(?:trattament\w*|applicazion\w*|interventi)(?:\s*(?:all|per)?\s*[\'’]?\s*(anno|ciclo\s+colturale|stagione))?',
    re.I)
RX_INTERVALO_APLIC = re.compile(
    r'(?:ogni|a\s+distanza\s+di|intervall\w*\s+(?:di|tra\s+i\s+trattamenti\s+di)?)\s*'
    r'(\d{1,2}(?:\s*[-–]\s*\d{1,2})?)\s*giorni', re.I)
RX_PHI = re.compile(
    r'(?:sospendere\s+i\s+trattamenti|intervallo\s+di\s+sicurezza|carenza)[^.\n]{0,60}?'
    r'(\d{1,3})\s*giorni(?:\s+prima\s+del(?:la)?\s+(raccolta|pascolamento|sfalcio))?', re.I)
RX_BBCH = re.compile(r'BBCH\s*(\d{2})(?:\s*[-–]\s*(?:BBCH\s*)?(\d{2}))?', re.I)
RX_EPOCA = re.compile(
    r'(pre[\s-]?emergenza|post[\s-]?emergenza(?:\s+(?:precoce|tardiva))?|pre[\s-]?semina|'
    r'pre[\s-]?trapianto|post[\s-]?trapianto|pre[\s-]?fioritura|post[\s-]?fioritura|'
    r'(?:dalla|alla|in)\s+(?:fase\s+di\s+)?(?:comparsa|ripresa\s+vegetativa|caduta\s+dei\s+petali|'
    r'fioritura|allegagione|invaiatura|germogliamento|chiusura\s+del\s+grappolo)'
    r'|alla\s+comparsa\s+de[il]\s+prim\w+\s+\w+|in\s+(?:autunno|primavera|inverno|estate)'
    r'|dopo\s+la\s+raccolta)', re.I)
RX_RESTRICAO = re.compile(
    r'(solo\s+(?:in\s+)?(?:serra|pieno\s+campo|ambiente\s+protetto|coltura\s+protetta)'
    r'|(?:uso\s+)?in\s+serra|in\s+pieno\s+campo|non\s+(?:ammess[oa]|consentit[oa]|autorizzat[oa])[^.\n]{0,60}'
    r'|non\s+impiegare[^.\n]{0,60}|vietat[oa][^.\n]{0,60}|da\s+non\s+(?:usare|impiegare)[^.\n]{0,60}'
    r'|fascia\s+di\s+rispetto[^.\n]{0,60}|zona\s+di\s+rispetto[^.\n]{0,60}'
    r'|solo\s+(?:per|su)\s+[^.\n]{3,40})', re.I)


def _f(x):
    return float(x.replace(',', '.')) if x else None


def _norm_unid(u):
    u = re.sub(r'\s+', '', (u or '').lower())
    u = re.sub(r'(di)?(p\.?f\.?|prodottoformulato|formulato)', 'pf', u)
    return u.replace('100lt', '100l').replace('100litri', '100l')


def doses_da_linha(texto, unidades_do_cabecalho=None):
    """→ [dose]. Dose com unidade escrita na linha = ENCONTRADO.

    Sem unidade na linha, só se aceita se o cabeçalho da tabela deu UMA unidade
    de dose: aí o primeiro número da linha herda-a, e a dose diz que herdou.
    Com duas ou mais unidades no cabeçalho, o número sem unidade não se atribui:
    é a geometria da página que sabe a coluna, e o texto corrido não.
    """
    doses = []
    for m in RX_DOSE.finditer(texto or ''):
        doses.append({'MIN': _f(m.group(1)), 'MAX': _f(m.group(2)) or _f(m.group(1)),
                      'UNIDADE': _norm_unid(m.group(3)), 'LITERAL': m.group(0).strip(),
                      'UNIDADE_HERDADA_DO_CABECALHO': False})
    # faixa invertida («75-19») não é dose: é número de outra coisa colado nela
    doses = [d for d in doses if d['MAX'] >= d['MIN']]
    if doses:
        return doses
    unids = list(dict.fromkeys(_norm_unid(u) for u in (unidades_do_cabecalho or [])))
    if len(unids) == 1:
        # tira os números que têm dono escrito ao lado: dias, meses, aplicações, BBCH
        sem_datas = re.sub(r'\d+(?:\s*[-–]\s*\d+)?\s*(?:giorni|gg\b|mesi|settiman\w*|ore\b|applicazion\w*|trattament\w*|interventi)'
                           r'|\(\s*\d+[^)]*\)'
                           r'|bbch\s*\d+(?:\s*[-–]\s*(?:bbch\s*)?\d+)?', ' ', texto or '', flags=re.I)
        cand = list(RX_FAIXA.finditer(sem_datas))
        # medido contra o leitor geométrico (IT-DOSES): «o primeiro número» errava
        # 361 de 761. Com dois ou mais números sem dono, o texto corrido não sabe a
        # coluna — e então não se atribui: NAO_CONHECIDO, não palpite.
        m = cand[0] if len(cand) == 1 else None
        if m:
            d = {'MIN': _f(m.group(1)), 'MAX': _f(m.group(2)) or _f(m.group(1)),
                 'UNIDADE': unids[0], 'LITERAL': m.group(0).strip(),
                 'UNIDADE_HERDADA_DO_CABECALHO': True}
            if d['MAX'] >= d['MIN']:
                doses.append(d)
    return doses


def campos_da_linha(texto, unidades_do_cabecalho=None):
    """→ dose, época, restrições, nº máximo, intervalo, carência — da LINHA só."""
    t = re.sub(r'[ \t]+', ' ', texto or '')
    fonte = 'rotulo:linha'
    doses = doses_da_linha(t, unidades_do_cabecalho)
    epocas = [m.group(0).strip() for m in RX_EPOCA.finditer(t)]
    bbch = [(m.group(1), m.group(2) or m.group(1)) for m in RX_BBCH.finditer(t)]
    rest = list(dict.fromkeys(m.group(0).strip(' ,;') for m in RX_RESTRICAO.finditer(t)))
    mx = RX_MAX_TRAT.search(t)
    iv = RX_INTERVALO_APLIC.search(t)
    phi = RX_PHI.search(t)
    return {
        'DOSE': campo(doses, ENCONTRADO, fonte) if doses else campo(None, NAO_CONHECIDO, fonte),
        'EPOCA': (campo({'LITERAL': epocas, 'BBCH': [{'DE': a, 'ATE': b} for a, b in bbch]},
                        ENCONTRADO, fonte) if (epocas or bbch) else campo(None, NAO_CONHECIDO, fonte)),
        'RESTRICOES': campo(rest, ENCONTRADO, fonte) if rest else campo(None, NAO_CONHECIDO, fonte),
        'MAX_APLICACOES': (campo({'N': int(mx.group(1)), 'POR': (mx.group(2) or None)},
                                 ENCONTRADO, fonte, mx.group(0)) if mx else campo(None, NAO_CONHECIDO, fonte)),
        'INTERVALO_ENTRE_APLICACOES': (campo(iv.group(1).replace(' ', '') + ' giorni', ENCONTRADO, fonte, iv.group(0))
                                       if iv else campo(None, NAO_CONHECIDO, fonte)),
        'INTERVALO_DE_SEGURANCA': (campo({'DIAS': int(phi.group(1)), 'ANTES_DE': phi.group(2)},
                                         ENCONTRADO, fonte, phi.group(0).strip())
                                   if phi else campo(None, NAO_CONHECIDO, fonte)),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 5. O RÓTULO INTEIRO → LINHAS DE USO
# ══════════════════════════════════════════════════════════════════════════════
def _unidades_do_cabecalho(cabecalho):
    return [m.group(0) for m in RX_UNIDADE.finditer(cabecalho)]


def _linhas_de_uso_cruas(texto):
    """→ [(cultura, alvo_literal, alvo_canonico, texto_da_linha, nivel, unidades_cab)].

    Três portas, pela ordem de força, todas de `rotulos_ler.py`:
      LINHA_DA_TABELA   a tabela une cultura e alvo na mesma linha
      BLOCO_DA_CULTURA  a cultura encabeça o bloco e o alvo vive dentro
    O herbicida (espectro solto) NÃO entra aqui: o par dele é declaração do
    produto, não linha de uso com dose — e não se finge que é.
    """
    saida = []
    for bloco in RL.regiao_da_tabela(texto):
        # o cabeçalho da tabela: as linhas logo acima do corpo, até à linha em branco
        cab_ini = texto.find(bloco)
        unids = _unidades_do_cabecalho(texto[max(0, cab_ini - 600):cab_ini].split('\n\n')[-1])
        for ln in RL.linhas_da_tabela(bloco):
            # a linha acaba na primeira linha em branco: o que vem depois é texto
            # do documento, não desta cultura
            corpo = []
            for x in ln['TEXTO']:
                if corpo and not x.strip():
                    break
                corpo.append(x)
            txt = re.sub(r'[ \t]+', ' ', '\n'.join(corpo)).strip()
            for lit, canon in RL.alvos_da_linha(txt):
                saida.append((ln['CULTURA_CANONICA'], lit, canon, txt, 'LINHA_DA_TABELA', unids))
    if saida:
        return saida
    for bloco in RL.regiao_de_impiego(texto):
        for cult, lit, canon, cit in RL.pares_do_bloco_de_cultura(bloco):
            saida.append((cult, lit, canon, cit, 'BLOCO_DA_CULTURA', []))
    if saida:
        return saida
    # a terceira porta: o bloco de cultura sem título de secção no texto extraído
    # (os rótulos de tau-fluvalinate que nomeiam o vetor da flavescência dourada)
    for bl in blocos_sem_cabecalho_cortados(texto):
        for lit, canon in RL.alvos_da_linha(bl['TEXTO']):
            saida.append((bl['CULTURA_CANONICA'], lit, canon, bl['TEXTO'], 'BLOCO_SEM_CABECALHO', []))
    return saida


def blocos_sem_cabecalho_cortados(texto):
    """`rotulos_ler.blocos_sem_cabecalho`, com o corpo cortado onde nasce o bloco seguinte.

    O corpo de lá são 8 linhas a partir do título da cultura. Medido nos 163
    rótulos reais em 26/09: em 38 de 102 blocos essas 8 linhas entram no bloco
    da cultura seguinte — a VITE do 007555 herdava «dorifora (Leptinotarsa)» e a
    dose da PATATA. Isso cria autorização que o rótulo não dá. Aqui o bloco
    acaba onde o próximo começa.

    Limite declarado: só corta no próximo bloco QUE FOI RECONHECIDO. Uma cultura
    seguinte sem «Contro…» logo abaixo não é bloco, e não serve de corte.
    """
    bls = RL.blocos_sem_cabecalho(texto)
    saida = []
    for i, bl in enumerate(bls):
        corpo = bl['TEXTO']
        if i + 1 < len(bls):
            j = corpo.find(bls[i + 1]['TEXTO'][:40], 5)
            if j > 0:
                corpo = corpo[:j].rstrip()
        saida.append({'CULTURA_CANONICA': bl['CULTURA_CANONICA'], 'TEXTO': corpo})
    return saida


def _mesmo_titular(a, b):
    """O nome curto (sem S.r.l./S.p.A./Ltd) de um está contido no outro."""
    corta = lambda s: re.sub(r'\b(s\.?\s*r\.?\s*l|s\.?\s*p\.?\s*a|ltd|gmbh|srl|spa|s\.?a)\b\.?', '', _n(s))
    a, b = re.sub(r'[^a-z0-9]', '', corta(a)), re.sub(r'[^a-z0-9]', '', corta(b))
    return bool(len(a) >= 4 and len(b) >= 4 and (a in b or b in a))


def ler_rotulo(dados, ficha, product_id=None, url=None, capturado_em=None):
    """Documento + ficha do registo → resultado canónico com as linhas de uso."""
    texto, doc = texto_do_documento(dados)
    doc.update(SOURCE_ID=SOURCE_ID_REGISTO, URL=url, CAPTURADO_EM=capturado_em)
    produto = {'PRODUCT_ID': campo(product_id, ENCONTRADO, 'chamador') if product_id
               else campo(None, NAO_CONHECIDO, 'chamador')}
    produto.update({k: v for k, v in ficha.items() if k != 'NO_REGISTO'})
    res = {'SCHEMA': SCHEMA, 'DOCUMENTO': doc, 'PRODUTO': produto, 'CABECALHO': {},
           'CONFERENCIA': {}, 'LINHAS_DE_USO': [], 'ESTADO_DA_LEITURA': None,
           'APROVACAO_UE_DA_SUBSTANCIA': 'campo separado: ver aprovacao_ue(); '
                                         'nunca escreve na autorizacao nacional',
           'AFIRMACAO_PROIBIDA': AFIRMACAO_PROIBIDA}
    if doc['ESTADO'] == ERRO:
        res['ESTADO_DA_LEITURA'] = ERRO
        return res

    cab = cabecalho_do_rotulo(texto)
    res['CABECALHO'] = cab
    doc['VERSAO'] = {'SHA256': doc['SHA256'],
                     'DATA_DO_DECRETO': cab['DATA_DO_DECRETO']['VALOR'],
                     'VALIDADE_DO_ROTULO': cab['VALIDADE_DO_ROTULO']['VALOR']}

    # ── conferência: é este o rótulo deste registo? ─────────────────────────
    conf = {}
    reg_ficha = ficha.get('NUMERO_REGISTO', {}).get('VALOR')
    reg_rot = cab['NUMERO_REGISTO_NO_ROTULO']['VALOR']
    if not ficha.get('NO_REGISTO'):
        conf['REGISTO'] = campo(None, NAO_CONHECIDO, 'registo oficial')
    elif reg_rot is None:
        conf['REGISTO'] = campo(reg_ficha, ENCONTRADO, 'registo oficial; o rotulo nao escreve o numero')
    elif reg_rot == reg_ficha:
        conf['REGISTO'] = campo(reg_ficha, VERIFICADO, 'registo oficial = rotulo')
    else:
        conf['REGISTO'] = campo({'REGISTO': reg_ficha, 'ROTULO': reg_rot}, ERRO,
                                'registo oficial != rotulo: documento de outro produto?')
    tit_rot = cab['TITULAR_NO_ROTULO']['VALOR']
    tit_reg = ficha.get('TITULAR', {}).get('VALOR')
    if tit_rot and tit_reg:
        conf['TITULAR'] = (campo(tit_reg, VERIFICADO, 'registo oficial = rotulo')
                           if _mesmo_titular(tit_rot, tit_reg)
                           else campo({'REGISTO': tit_reg, 'ROTULO': tit_rot}, ERRO, 'registo oficial != rotulo'))
    elif tit_reg and _mesmo_titular(tit_reg, texto[:4000]):
        # medido: 0 de 60 rótulos escrevem «Titolare»; o nome da empresa vem no
        # topo. O nome do registo escrito no documento é a segunda fonte.
        conf['TITULAR'] = campo(tit_reg, VERIFICADO, 'nome do titular do registo escrito no rotulo')
    elif tit_reg:
        conf['TITULAR'] = campo(tit_reg, ENCONTRADO, 'registo oficial; o rotulo nao escreve o titular')
    res['CONFERENCIA'] = conf

    documento_deste_registo = conf['REGISTO']['ESTADO'] == VERIFICADO
    if conf['REGISTO']['ESTADO'] == ERRO:
        # rótulo de outro produto: nenhuma linha dele se atribui a este registo
        res['ESTADO_DA_LEITURA'] = ERRO
        return res
    if documento_deste_registo:
        for k in ('NUMERO_REGISTO', 'PRODUTO', 'TITULAR', 'PRINCIPIOS_ATIVOS', 'FORMULACAO'):
            if produto.get(k, {}).get('ESTADO') == ENCONTRADO:
                produto[k] = dict(produto[k], ESTADO=VERIFICADO,
                                  FONTE=produto[k]['FONTE'] + ' + rotulo com o mesmo numero')
    if conf.get('TITULAR', {}).get('ESTADO') == ERRO:
        produto['TITULAR'] = conf['TITULAR']

    # ── linhas de uso ────────────────────────────────────────────────────────
    vistos = set()
    for cult, lit, canon, txt, nivel, unids in _linhas_de_uso_cruas(texto):
        chave = (cult, lit.lower(), txt)
        if chave in vistos:
            continue
        vistos.add(chave)
        estado_par = VERIFICADO if (documento_deste_registo and nivel == 'LINHA_DA_TABELA') else ENCONTRADO
        linha = {
            'PRODUCT_ID': produto['PRODUCT_ID']['VALOR'],
            'NUMERO_REGISTO': reg_ficha,
            'VERSAO_DO_DOCUMENTO': doc['VERSAO'],
            'CULTURA': campo({'CANONICA': cult}, estado_par, 'rotulo:' + nivel),
            'ALVO': campo({'LITERAL': lit, 'CANONICO': canon}, estado_par, 'rotulo:' + nivel),
            'LIGACAO_NIVEL': nivel,
            'CITACAO_DA_LINHA': txt[:900],
            'VALIDADE_DA_AUTORIZACAO': produto['VALIDADE_DA_AUTORIZACAO'],
            'AUTORIZACAO_NACIONAL_VIVA': produto['AUTORIZACAO_NACIONAL_VIVA'],
        }
        linha.update(campos_da_linha(txt, unids))
        res['LINHAS_DE_USO'].append(linha)

    res['ESTADO_DA_LEITURA'] = ENCONTRADO if res['LINHAS_DE_USO'] else NAO_CONHECIDO
    if not res['LINHAS_DE_USO']:
        res['MOTIVO'] = ('nenhuma linha de uso lida neste documento. Isto e limite do '
                         'leitor, nao prova regulatoria.')
    return res


# ══════════════════════════════════════════════════════════════════════════════
# 6. APROVAÇÃO UE DA SUBSTÂNCIA — outro campo, outra fonte, outra pergunta
# ══════════════════════════════════════════════════════════════════════════════
def aprovacao_ue(substancia, atos_json=EU_ATOS):
    """→ campo com os atos europeus de 2026 cujo título nomeia a substância.

    ENCONTRADO = há ato que a nomeia (não diz se aprova, renova ou retira: lê-se o
    título). NAO_CONHECIDO = não achámos NESTA amostra — não é «não aprovada».
    Em nenhum caso isto muda AUTORIZACAO_NACIONAL_VIVA.
    """
    fonte = 'EU-T4-001 · amostra SPARQL CELLAR 2026'
    try:
        with open(atos_json, encoding='utf-8') as fh:
            d = json.load(fh)
    except (OSError, ValueError) as e:
        return campo(None, ERRO, fonte, '%s: %s' % (type(e).__name__, e))
    alvo = _n(substancia).strip()
    if not alvo:
        return campo(None, NAO_CONHECIDO, fonte)
    atos = []
    for b in d.get('sparql_results', {}).get('results', {}).get('bindings', []):
        tit = b.get('title', {}).get('value', '')
        if re.search(r'(?<![a-z])' + re.escape(alvo) + r'(?![a-z])', _n(tit)):
            atos.append({'CELEX': b.get('celex', {}).get('value'),
                         'DATA': b.get('date', {}).get('value'), 'TITULO': tit})
    return campo(atos, ENCONTRADO, fonte) if atos else campo(None, NAO_CONHECIDO, fonte)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('documento')
    ap.add_argument('--registo', required=True)
    ap.add_argument('--csv', default=CSV_REGISTO)
    ap.add_argument('--product-id')
    ap.add_argument('--url')
    a = ap.parse_args(argv)
    ficha = ficha_do_registo(ler_registo(a.csv), a.registo,
                             snapshot=os.path.splitext(os.path.basename(a.csv))[0])
    with open(a.documento, 'rb') as f:
        res = ler_rotulo(f.read(), ficha, product_id=a.product_id, url=a.url)
    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
    print()
    return 0 if res['ESTADO_DA_LEITURA'] != ERRO else 2


if __name__ == '__main__':
    sys.exit(main())
