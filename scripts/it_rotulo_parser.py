#!/usr/bin/env python3
"""Parser de etichetta ADAMA Italia: extrai CULTURA x ALVO sem inventar relacao.

O DEFEITO QUE ESTE PARSER EXISTE PARA CORRIGIR
----------------------------------------------
O conjunto anterior tinha 2.030 pares e perdia sistematicamente:

    PERO   47 rotulos no texto ->  4 pares      OLIVO 15 -> 1
    VITE   72                  -> 25            NOCE  19 -> 0
    POMODORO 55                -> 18            NOCCIOLO 17 -> 0

A causa: `pdftotext -layout` achata COLUNAS. Num rotulo de tres colunas a cultura fica
numa faixa de x, o alvo noutra, e prosa de seguranca numa terceira — e as tres caem na
mesma linha do arquivo. Casar por proximidade nesse texto e casar por acaso.

A CORRECAO: ler GEOMETRIA. `pdftotext -bbox-layout` da blocos e linhas com coordenadas.
Uma tabela afirma que a cultura da esquerda vale para os alvos que estao NA MESMA FAIXA
VERTICAL a direita dela. Essa e a relacao que o documento realmente faz, e e a unica
que este parser aceita da tabela.

DUAS ROTAS, porque os 163 rotulos tem duas familias de forma:
  GEOMETRICA  celula de cultura + celulas de alvo na mesma faixa (25 rotulos)
  INLINE      "Cultura: contro Alvo ..." / "Su CULTURA: ..." (o resto)

O QUE ELE NAO FAZ, DE PROPOSITO
  - nao expande grupo de cultura sem enumeracao explicita no proprio rotulo;
  - nao promove nome comum a identidade taxonomica;
  - nao casa substancia por parecenca (so pela tabela de normalizacao com fonte);
  - nao transforma frase de restricao em autorizacao.
"""
import html
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from it_rotulo_vocab import (ALVOS, CULTURAS, GRUPOS, SUBSTANCIA_NORM,  # noqa: E402
                             TAXONOMIA)

PARSER_VERSION = 'it_rotulo_parser/3.2.0'

CROP_RX = {k: re.compile(r'\b(?:%s)' % '|'.join(v), re.I) for k, v in CULTURAS.items()}
TGT_RX = {k: re.compile(r'\b(?:%s)' % '|'.join(v), re.I) for k, v in ALVOS.items()}
GRUPO_RX = re.compile(r'\b(%s)\b\s*\(([^)]{5,300})\)' % '|'.join(GRUPOS), re.I)

# Secoes que NAO produzem par: descricao comercial, seguranca, medico, fitotoxicidade,
# e a tabela de carenza (que lista cultura sem alvo).
SECAO_PROIBIDA = re.compile(
    r'CARATTERISTICHE|CONSIGLI\s+DI\s+PRUDENZA|INDICAZIONI\s+DI\s+PERICOLO|'
    r'INFORMAZIONI\s+PER\s+IL\s+MEDICO|FITOTOSSICIT|PRESCRIZIONI\s+SUPPLEMENTARI|'
    r'Intervallo\s+tra\s+l.?ultimo\s+trattamento\s+e\s+la\s+raccolta|'
    r'Stabiliment[oi]\s+di|SMALTIMENTO|MECCANISMO\s+D.?AZIONE|COMPATIBILIT', re.I)

# Frase que NEGA o uso.
EXCLUSAO = re.compile(
    r'non\s+(?:applicare|impiegare|utilizzare|trattare)|'
    r'divieto\s+di|non\s+autorizzat\w*|evitare\s+(?:\w+\s+){0,2}?deriva|'
    r'\bderiva\s+(?:verso|su)\b|'
    r'colt(?:ure|ivazioni)\s+(?:adiacenti|limitrofe|successive)|'
    r'sono\s+sensibili\s+al\s+prodotto|'
    r'sostituzione\s+della\s+coltura|fallimento\s+della\s+coltura|'
    r'fascia\s+di\s+sicurezza\s+di\s+\d|in\s+prossimit[aà]', re.I)

# Marcadores de que a frase e mesmo uma DECLARACAO DE USO.
# FIX-A. 'malattie fungine', 'patologie', 'malerbe' sao CATEGORIAS: dizem de que
# TIPO de inimigo o produto trata, e nao QUAL inimigo. A frase
# 'Intervenire ... per il controllo delle malattie fungine dell'orzo' declara ESCOPO
# (item 5: CROP_SCOPE_DECLARED), e nao autorizacao de par. Publicar
# ORZO x MALATTIE_FUNGINE ao lado de ORZO x RAMULARIA duplicaria a mesma autorizacao
# com um nome vago — foi medido como falso positivo em AVASTEL (018089).
ALVO_CATEGORIA = {'MALATTIE_FUNGINE'}

# O mesmo raciocinio do lado da CULTURA. 'Pomacee', 'Drupacee', 'Cucurbitacee' sao
# GRUPOS. Ou o rotulo enumera os membros entre parenteses — e ai o par sai para cada
# membro enumerado — ou o grupo fica sem resolucao e nao vira par. Publicar
# CUCURBITACEE x AFIDI ao lado de MELONE x AFIDI contaria a mesma autorizacao duas
# vezes, e num rotulo que nao enumera inventaria membros que a etiqueta nao nomeia.
CULTURA_CATEGORIA = set(GRUPOS)

USO = re.compile(
    r'\bcontro\b|per\s+il\s+(?:controllo|diserbo)|\bdose\b|\bdosi\b|l/ha|kg/ha|l/hl|'
    r'ml/hl|g/hl|intervenire|applicare|impiegare|trattament\w*|pre-?emergenza|'
    r'post-?emergenza', re.I)


# ── geometria ─────────────────────────────────────────────────────────────────
def bbox_xml(pdf, dest):
    if not os.path.exists(dest) or os.path.getsize(dest) < 200:
        subprocess.run(['pdftotext', '-bbox-layout', pdf, dest],
                       capture_output=True, timeout=240)
    return dest


GEOMETRIA_VERSIONADA = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1/geometria')


def geometria_de(rid, fallback_pdf=None, cache_dir=None):
    """Prefere a geometria VERSIONADA. Sem ela, deriva do PDF.

    A geometria e a entrada REAL do parser. Guardada em git (gzip), um contêiner novo
    reproduz o conjunto de pares sem rede e sem PDF — que e o que a missao exige depois
    de tres perdas seguidas por arquivo nao commitado.
    """
    gz = os.path.join(GEOMETRIA_VERSIONADA, '%s.xml.gz' % rid)
    if os.path.exists(gz):
        return gz
    if fallback_pdf and os.path.exists(fallback_pdf):
        return bbox_xml(fallback_pdf, os.path.join(cache_dir or os.path.dirname(
            fallback_pdf), '%s.xml' % rid))
    return None


def ler_geometria(xml_path):
    """-> [{page, x0,y0,x1,y1, text, lines:[{y0,y1,text}]}]"""
    if xml_path.endswith('.gz'):
        import gzip
        raw = gzip.open(xml_path, 'rt', encoding='utf-8', errors='replace').read()
    else:
        raw = open(xml_path, encoding='utf-8', errors='replace').read()
    if raw.startswith('<!DOCTYPE'):
        raw = raw.split('>', 1)[1]
    raw = re.sub(r'\sxmlns="[^"]*"', '', raw, count=1)
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        root = ET.fromstring(re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', raw))
    out = []
    for pi, page in enumerate(root.iter('page')):
        for b in page.iter('block'):
            lines = []
            for ln in b.iter('line'):
                t = ' '.join(w.text or '' for w in ln.iter('word')).strip()
                if t:
                    lines.append({'y0': float(ln.get('yMin')), 'y1': float(ln.get('yMax')),
                                  'text': html.unescape(t)})
            if not lines:
                continue
            out.append({'page': pi, 'x0': float(b.get('xMin')), 'y0': float(b.get('yMin')),
                        'x1': float(b.get('xMax')), 'y1': float(b.get('yMax')),
                        'lines': lines,
                        'text': ' '.join(l['text'] for l in lines)})
    return out


# ── vocabulario ───────────────────────────────────────────────────────────────
def culturas_em(txt):
    return sorted({k for k, rx in CROP_RX.items() if rx.search(txt)})


def alvos_em(txt):
    return sorted({k for k, rx in TGT_RX.items() if rx.search(txt)})


def expandir_grupos(txt):
    """'Pomacee (melo, pero, ...)' -> membros ENUMERADOS pelo proprio rotulo.

    Grupo sem enumeracao entre parenteses NAO e expandido: seria inventar cobertura.
    """
    achados = []
    for m in GRUPO_RX.finditer(txt):
        membros = culturas_em(m.group(2))
        if membros:
            achados.append({'GRUPO': m.group(1).upper(), 'MEMBROS': membros,
                            'ENUMERACAO_NO_ROTULO': m.group(2)[:200]})
    return achados


def status_taxonomico(raw):
    for t in TAXONOMIA:
        if re.search(re.escape(t['RAW_TARGET_NAME']), raw, re.I):
            return t['TAXONOMIC_STATUS'], t['NOTA']
    return 'UNKNOWN', None


def normalizar_substancia(raw):
    for s in SUBSTANCIA_NORM:
        if re.search(r'\b%s\b' % re.escape(s['RAW_TERM']), raw, re.I):
            return s
    return None


# ── rota GEOMETRICA (tabela) ──────────────────────────────────────────────────
def _entradas(bloco):
    """Agrupa linhas de um bloco de alvo em ENTRADAS.

    Uma entrada e uma unidade semantica que pode ocupar varias linhas. Linhas de
    continuacao (comecam com minuscula, com '(' ou com conectivo) pertencem a entrada
    anterior. Sem isso, a primeira linha de uma entrada de tres linhas cai na faixa da
    cultura de cima e o par sai trocado — foi medido.
    """
    ents, cur = [], None
    abre = False
    for ln in bloco['lines']:
        t = ln['text'].strip()
        cont = bool(re.match(r'^[\(a-zàèéìòù]', t)) or bool(
            re.match(r'^(?:e|ed|o|od|della|del|di|in|con|gen\.?)\b', t, re.I))
        # Uma linha que TERMINA em ':' e cabecalho: as linhas seguintes sao dela.
        # Sem isto 'Tignola e tignoletta:' virava entrada sozinha, o seu centro caia
        # na faixa da cultura de cima, e o nocciolo herdava a tignola da vite.
        cont = cont or abre
        abre = t.endswith(':')
        if cur and cont:
            cur['lines'].append(t)
            cur['y1'] = ln['y1']
        else:
            if cur:
                ents.append(cur)
            cur = {'y0': ln['y0'], 'y1': ln['y1'], 'lines': [t]}
    if cur:
        ents.append(cur)
    for e in ents:
        e['text'] = ' '.join(e['lines'])
        e['yc'] = (e['y0'] + e['y1']) / 2.0
    return ents


def pares_geometricos(blocos):
    """Celula de cultura a esquerda + alvos na MESMA FAIXA a direita."""
    pares = []
    for pg in sorted({b['page'] for b in blocos}):
        pb = [b for b in blocos if b['page'] == pg]
        # celulas de cultura: bloco CURTO, dominado por nome de cultura
        cells = []
        for b in pb:
            t = b['text']
            if len(t) > 110:
                continue
            cs = culturas_em(t)
            if not cs:
                continue
            # a celula tem de ser majoritariamente o nome da cultura, e nao prosa
            if len(t) > 12 + 14 * len(cs) + 30:
                continue
            if SECAO_PROIBIDA.search(t):
                continue
            cells.append({'crops': cs, 'b': b, 'yc': (b['y0'] + b['y1']) / 2.0})
        if not cells:
            continue
        # colunas: agrupa celulas de cultura por faixa de x parecida
        cells.sort(key=lambda c: (round(c['b']['x0'] / 40), c['yc']))
        colunas = {}
        for c in cells:
            colunas.setdefault(round(c['b']['x0'] / 40), []).append(c)
        for col in colunas.values():
            col.sort(key=lambda c: c['yc'])
            # ⚠️ TABELA DE LINHA UNICA. Antes eu exigia len(col) >= 2, e uma tabela
            # com UMA linha era descartada inteira. Isso zerava SPYRALE (009757),
            # que declara "Barbabietola da zucchero" numa celula e
            # "Cercosporiosi | Oidio" na celula ao lado — uma tabela perfeitamente
            # legivel, com um so par de linhas.
            #
            # A guarda existia por um motivo real: sem uma celula vizinha nao ha
            # como inferir onde a linha termina. Entao a regra da linha unica e
            # MAIS ESTREITA, e nao igual: a faixa e a propria altura da celula
            # mais uma tolerancia do tamanho dela. O que cair fora disso vira
            # AMBIGUOUS_ROW, nunca SUPPORTED_PAIR.
            unica = len(col) == 1
            # faixa de cada cultura = do meio-caminho com a de cima ao meio-caminho
            # com a de baixo. A celula fica CENTRADA na sua linha, e nao no topo.
            bandas = []
            for i, c in enumerate(col):
                if unica:
                    alt = max(14.0, c['b']['y1'] - c['b']['y0'])
                    topo, base = c['b']['y0'] - alt, c['b']['y1'] + alt
                else:
                    topo = (col[i - 1]['yc'] + c['yc']) / 2 if i else c['yc'] - 60
                    base = (c['yc'] + col[i + 1]['yc']) / 2 if i + 1 < len(col) \
                        else c['yc'] + 60
                bandas.append((topo, base, c))
            xmax = max(c['b']['x1'] for c in col)
            # ESCOPO DE COLUNA. Um bloco a direita nao basta: rotulos grandes tem DUAS
            # tabelas lado a lado, cada uma com a sua coluna de cultura. Pegar "tudo o
            # que esta a direita" fez VITE herdar Dorifora da tabela das orticolas —
            # medido contra o gabarito. O alvo tem de ficar ANTES da proxima coluna de
            # cultura e perto da sua propria.
            outras = [c['b']['x0'] for c in cells if c['b']['x0'] > xmax + 20]
            limite = min(outras) if outras else float('inf')
            alvos_blocos = [b for b in pb
                            if xmax < b['x0'] < min(limite, xmax + 260)
                            and not SECAO_PROIBIDA.search(b['text'])]
            for ab in alvos_blocos:
                for ent in _entradas(ab):
                    tg = alvos_em(ent['text'])
                    if not tg:
                        continue
                    excl = bool(EXCLUSAO.search(ent['text']))
                    for topo, base, c in bandas:
                        if topo <= ent['yc'] < base:
                            # A fronteira entre linhas da tabela e inferida (o PDF nao
                            # entrega os fios da grade). Quando a entrada cai COLADA na
                            # fronteira, a atribuicao e um chute: declaro AMBIGUOUS_ROW
                            # em vez de afirmar. Foi assim que o nocciolo deixou de
                            # herdar a tignola da vite.
                            # Regra: se o centro da entrada cai DENTRO da extensao
                            # vertical da propria celula de cultura, a atribuicao e
                            # firme. Se cai fora, comparo a distancia ate a celula com
                            # a distancia ate a fronteira inferida: mais perto da
                            # fronteira = chute, e ai declaro AMBIGUOUS_ROW.
                            cy0, cy1 = c['b']['y0'], c['b']['y1']
                            dentro = cy0 <= ent['yc'] <= cy1
                            d_cel = 0 if dentro else min(abs(ent['yc'] - cy0),
                                                         abs(ent['yc'] - cy1))
                            d_bor = min(abs(ent['yc'] - topo), abs(ent['yc'] - base))
                            margem = round(d_bor - d_cel, 1)
                            rel = ('EXCLUDED_PAIR' if excl
                                   else 'SUPPORTED_PAIR' if (dentro or d_cel < d_bor)
                                   else 'AMBIGUOUS_ROW')
                            for crop in c['crops']:
                                for t in tg:
                                    pares.append({
                                        'CROP': crop, 'TARGET': t,
                                        'ROUTE': 'GEOMETRIC_TABLE',
                                        'RELATION': rel,
                                        'ROW_MARGIN': round(margem, 1),
                                        'CROP_AS_WRITTEN': c['b']['text'][:80],
                                        'TARGET_AS_WRITTEN': ent['text'][:180],
                                        'PAGE': pg,
                                        'CROP_Y': [round(c['b']['y0'], 1),
                                                   round(c['b']['y1'], 1)],
                                        'TARGET_Y': [round(ent['y0'], 1),
                                                     round(ent['y1'], 1)],
                                    })
                            break
    return pares


# ── rota INLINE (prosa) ───────────────────────────────────────────────────────
INLINE_RX = re.compile(
    r'(?:^|[.;)]\s|\n)\s*((?:[A-ZÀ-Ü][\wàèéìòùA-Za-z]*'
    r'(?:\s*\([^)]{0,120}\))?)(?:\s*(?:,|\be\b|\bed\b)\s*'
    r'[A-ZÀ-Ü]?[\wàèéìòùA-Za-z]+(?:\s*\([^)]{0,120}\))?){0,4})\s*'
    r'(?:\(in [^)]{0,60}\)\s*)?[:\-–]\s*(?:contro\s+)?([^\n]{6,420})')

SU_RX = re.compile(r'\bSu\s+([A-ZÀ-Ü][A-ZÀ-Ü ,]{2,80}?)\s*:\s*([^\n]{6,420})')


def _cabecas_por_dois_pontos(txt):
    """Toda declaracao de uso destes rotulos e '<cabeca> : <declaracao>'.

    A cabeca nem sempre comeca depois de ponto: em 012573 o rotulo escreve
    '... in inverno OLIVO (olive da tavola e da mensa): contro Cocciniglie e Tignole'.
    Um regex ancorado em inicio de frase perde isso — e perdeu, contra o gabarito.

    Entao: para cada ':', olho a janela ANTES dele e exijo que a cultura esteja PERTO
    do ':' (<= 70 caracteres). Longe demais e outra frase, e associar seria proximidade
    textual — exatamente o que esta casa proibe.
    """
    for m in re.finditer(r':', txt):
        i = m.start()
        ini = max(0, i - 95)
        jan = txt[ini:i]
        corte = max(jan.rfind('.'), jan.rfind(';'), jan.rfind('•'))
        if corte >= 0:
            jan = jan[corte + 1:]
        if not jan.strip():
            continue
        cab = _run_de_culturas_antes_do_dois_pontos(jan)
        if not cab:
            continue
        yield cab, _ate_a_proxima_cabeca(txt[i + 1:i + 1 + 420])


def _run_de_culturas_antes_do_dois_pontos(jan):
    """So o RUN de culturas colado ao ':' — nao toda cultura da vizinhanca.

    Pegar 'todas as culturas nos 95 caracteres antes do :' multiplicava tudo por tudo:
    num bloco denso como o do EKO OIL SPRAY, o olivo herdava os alvos do fico e do
    ribes. Aqui eu ando PARA TRAS a partir do ':' aceitando apenas nomes de cultura e
    separadores; o primeiro token que nao e nenhum dos dois encerra o cabecalho.
    """
    j = jan.rstrip()
    # FIX-C. Entre a lista de culturas e o ':' cabe um qualificador de LOCAL ou de
    # ESTADO — 'in campo aperto e serra', '(uso in serra)', 'in pieno campo'. Ele nao
    # e cultura nem separador, entao encerrava o cabecalho e a declaracao inteira se
    # perdia: era assim que APYZA (018156/018165) perdia a linha das cucurbitacee.
    # Removo o qualificador; ele nao muda QUEM e a cultura, so ONDE se aplica.
    j = re.sub(r'\s*\(?\b(?:uso\s+)?in\s+(?:pieno\s+campo|campo\s+aperto|campo|'
               r'serra|vivaio|vivai)(?:\s+(?:e|ed|o)\s+(?:pieno\s+campo|'
               r'campo\s+aperto|campo|serra|vivaio|vivai))*\)?\s*$', '', j, flags=re.I)
    # O parentetico final so cai quando NAO enumera culturas. Em
    # 'OLIVO (olive da tavola e da mensa)' ele e qualificador e sai; em
    # 'Cucurbitacee (melone, cetriolo, cocomero, zucchino)' ele E a enumeracao que
    # autoriza expandir o grupo, e tirá-lo publicaria o grupo sem os membros.
    # Quando o parentetico final ENUMERA culturas ele e a autorizacao, e nao um
    # qualificador: 'POMACEE (Melo, Pero e Cotogno)'. Tiro-o do texto MAS guardo os
    # membros, senao a caminhada para tras tropeca no primeiro nome de fora do
    # vocabulario ('Cotogno') e a declaracao inteira se perde — foi o que fazia
    # OLIONET e EKO OIL SPRAY perderem melo, pero, vite e agrumi.
    do_parentetico = []
    m_par = re.search(r'\s*\(([^()]{0,200})\)\s*$', j)
    if m_par:
        do_parentetico = culturas_em(m_par.group(1))
        j = j[:m_par.start()]
    toks = re.findall(r'[^\s,;]+|,|;', j)
    # Qualificadores de cultura ('VITE da VINO', 'BARBABIETOLA da ZUCCHERO', 'Orzo
    # invernale') nao podem encerrar o cabecalho: sem isto o SOLOFOL perdia
    # 'VITE da VINO: contro Peronospora, Botrite' inteiro — medido.
    sep = re.compile(r'^(?:,|;|e|ed|o|od|da|di|del|della|in|su|il|la|le|lo|i|gli|'
                     r'vino|tavola|zucchero|foraggio|invernale|primaverile|tenero|'
                     r'duro|dolce|rossa|rosso|olio|mensa)$', re.I)
    achados, i = list(do_parentetico), len(toks) - 1
    grupo_rx = re.compile(r'^(?:%s)$' % '|'.join(GRUPOS), re.I)
    while i >= 0:
        t = toks[i]
        if sep.match(t):
            i -= 1
            continue
        # O nome do GRUPO nao e cultura, mas tambem nao encerra a cabeca: ele e o
        # rotulo da enumeracao que eu acabei de ler entre parenteses.
        if grupo_rx.match(t) and do_parentetico:
            i -= 1
            continue
        cs = culturas_em(t)
        if not cs:
            break
        achados.extend(cs)
        i -= 1
    return ' '.join(sorted(set(achados))) if achados else None


def _ate_a_proxima_cabeca(resto):
    """Corta a declaracao onde comeca a PROXIMA cultura.

    Sem isto, a janela de 420 caracteres de 'OLIVO ...: contro Cocciniglie e Tignole'
    invadia a entrada seguinte ('FICO, CACO, RIBES, NOCE, NOCCIOLO: contro Acari,
    Afidi, ...') e o olivo herdava oito alvos que nao sao dele. Medido contra o gabarito.
    """
    fim = len(resto)
    for rx in CROP_RX.values():
        for m in rx.finditer(resto):
            j = m.start()
            if j == 0:
                continue
            # so corta se essa cultura for CABECA de outra declaracao (tem ':' logo apos)
            if ':' in resto[m.end():m.end() + 90]:
                fim = min(fim, j)
    return resto[:fim]


def _enumeracao_pura_de_alvos(resto):
    """True quando 'resto' e uma LISTA de alvos e nada mais.

    Criterio: tirados os parenteses (nomes cientificos) e a pontuacao, cada fragmento
    separado por virgula ou 'e' ou tem termo de alvo, ou e vazio/ruido curto. Basta um
    fragmento com prosa de verdade para recusar — assim a regra le celula de tabela
    sem abrir a porta para casar alvo com qualquer frase vizinha.
    """
    r = re.sub(r'\([^()]*\)', ' ', resto)
    r = re.split(r'[.;•]', r)[0]
    frags = [f.strip() for f in re.split(r',|\be\b|\bed\b', r) if f.strip()]
    if not frags or len(frags) > 12:
        return False
    com_alvo = 0
    for f in frags:
        if len(f) > 60:
            return False
        if alvos_em(f):
            com_alvo += 1
        elif len(re.findall(r"[A-Za-zÀ-ÿ']{3,}", f)) > 2:
            return False       # prosa
    return com_alvo >= 1


def pares_inline(blocos):
    pares = []
    for b in blocos:
        if SECAO_PROIBIDA.search(b['text']):
            continue
        txt = b['text']
        fontes = [(INLINE_RX, 'INLINE_STATEMENT'), (SU_RX, 'INLINE_SU_CROP')]
        achados = [(c, r, rota) for rx, rota in fontes for m in rx.finditer(txt)
                   for c, r in [(m.group(1), m.group(2))]]
        achados += [(c, r, 'INLINE_COLON_HEAD') for c, r in _cabecas_por_dois_pontos(txt)]
        for cabeca, resto, rota in achados:
            if True:
                crops = culturas_em(cabeca)
                # grupo com enumeracao explicita no proprio rotulo
                for g in expandir_grupos(cabeca):
                    crops = sorted(set(crops) | set(g['MEMBROS']))
                if not crops:
                    continue
                # FIX-B. Numa TABELA a celula e so '<culturas>: <lista de doencas>',
                # sem 'contro' e sem dose: quem da o sentido de uso e o cabecalho da
                # coluna ('Coltura | Malattia'). Exigir verbo de uso zerava SEEDRON
                # (016152), que escreve 'Orzo: Fusariosi (...), Carbone (...)'.
                # Aceito a ausencia do verbo SO quando o resto e enumeracao PURA de
                # alvos: cada fragmento separado por virgula, tirados os parenteses,
                # e um termo de alvo ou vazio. Prosa nao passa por aqui.
                if not USO.search(resto) and not _enumeracao_pura_de_alvos(resto):
                    continue
                tg = alvos_em(resto)
                if not tg:
                    continue
                excl = bool(EXCLUSAO.search(resto))
                for c in crops:
                    for t in tg:
                        pares.append({
                            'CROP': c, 'TARGET': t, 'ROUTE': rota,
                            'RELATION': 'EXCLUDED_PAIR' if excl else 'SUPPORTED_PAIR',
                            'CROP_AS_WRITTEN': cabeca.strip()[:80],
                            'TARGET_AS_WRITTEN': resto.strip()[:180],
                            'PAGE': b['page'],
                            'CROP_Y': [round(b['y0'], 1), round(b['y1'], 1)],
                            'TARGET_Y': [round(b['y0'], 1), round(b['y1'], 1)],
                        })
    return pares


# ── rota HEADER_CONTINUATION ──────────────────────────────────────────────────
ABRE_USO = re.compile(r'^\s*(?:contro\b|per\s+il\s+controllo\b|per\s+combattere\b|'
                      r'impiegare\b|intervenire\b|si\s+impiega\b)', re.I)


def pares_header_continuation(blocos):
    """Cabecalho de cultura, QUEBRA DE LINHA, e a declaracao de uso abaixo. Sem ':'.

        Pomacee (melo, pero, melo cotogno e nespolo)
        Contro afidi (Dysaphis plantaginea, Aphis pomi), ditteri cecidomidi ...

    Regra ESTRUTURAL, e nao caso especial de produto: a cabeca sao as linhas iniciais
    do bloco ate a primeira linha que ABRE uma declaracao de uso. A relacao vive
    dentro do bloco e morre nele — nao atravessa secao nem outro cabecalho.
    """
    pares = []
    for b in blocos:
        if len(b['lines']) < 2 or SECAO_PROIBIDA.search(b['text']):
            continue
        k = next((i for i, ln in enumerate(b['lines']) if ABRE_USO.match(ln['text'])), None)
        if not k:                       # 0 tambem e falso: precisa de cabeca antes
            continue
        cabeca = ' '.join(ln['text'] for ln in b['lines'][:k])
        if len(cabeca) > 220 or ':' in cabeca:
            continue                    # com ':' e a rota inline; longo demais e prosa
        crops = culturas_em(cabeca)
        for g in expandir_grupos(cabeca):
            crops = sorted(set(crops) | set(g['MEMBROS']))
        if not crops:
            continue
        # a declaracao vai ate o fim do bloco ou ate a proxima cabeca de cultura
        resto = ' '.join(ln['text'] for ln in b['lines'][k:])
        tg = alvos_em(resto)
        if not tg:
            continue
        excl = bool(EXCLUSAO.search(resto))
        for c in crops:
            for t in tg:
                pares.append({
                    'CROP': c, 'TARGET': t, 'ROUTE': 'HEADER_CONTINUATION',
                    'RELATION': 'EXCLUDED_PAIR' if excl else 'SUPPORTED_PAIR',
                    'CROP_AS_WRITTEN': cabeca.strip()[:110],
                    'TARGET_AS_WRITTEN': resto.strip()[:200],
                    'PAGE': b['page'],
                    'CROP_Y': [round(b['y0'], 1), round(b['y1'], 1)],
                    'TARGET_Y': [round(b['y0'], 1), round(b['y1'], 1)],
                })
    return pares


# ── rota SCOPE (tres niveis, conforme a missao exige) ─────────────────────────
ESCOPO_CULTURA = re.compile(
    r'(?:diserbante|erbicida|fungicida|insetticida|acaricida|molluschicida|'
    r'geodisinfestante|prodotto)\b[^.]{0,140}?\b(?:per|della|delle|del|dei|su)\b'
    r'[^.]{0,160}', re.I)
ESCOPO_ALVO_GLOBAL = re.compile(
    r'infestanti\s+(?:controllate|sensibili)|malerbe\s+controllate|'
    r'per\s+il\s+controllo\s+di\s+infestanti|spettro\s+d.?azione', re.I)
CATEGORIA_ERBICIDA = re.compile(r'diserbante|erbicida', re.I)


def escopos(blocos, categoria_produto=None):
    """CROP_SCOPE_DECLARED e TARGET_DECLARED — separados, como a missao manda.

    Uma frase como 'Fungicida per la difesa della BARBABIETOLA dalle malattie fungine'
    prova que a cultura esta no escopo. NAO prova cada doenca individual. Por isso o
    par so nasce quando o alvo tambem esta declarado, e mesmo assim ele sai marcado
    como SCOPE_COMBINATION — nunca como se fosse uma linha de tabela.
    """
    crop_scope, target_scope, frases = set(), set(), []
    for b in blocos:
        if SECAO_PROIBIDA.search(b['text']):
            continue
        for m in ESCOPO_CULTURA.finditer(b['text']):
            cs = culturas_em(m.group(0))
            if cs:
                crop_scope |= set(cs)
                frases.append(m.group(0)[:180])
        if ESCOPO_ALVO_GLOBAL.search(b['text']):
            target_scope |= set(alvos_em(b['text']))
            frases.append(b['text'][:180])
    herbicida = bool(categoria_produto and CATEGORIA_ERBICIDA.search(categoria_produto))
    return crop_scope, target_scope, frases, herbicida


# FIX-D. A LISTA DE USOS AUTORIZADOS.
#
# Muitos herbicidas escrevem o alvo uma vez, para o documento inteiro
# ('Infestanti controllate: ...'), e depois listam as culturas num bloco proprio —
# ou como enumeracao ('Usi autorizzati: frumento, orzo, mais, cipolla, olivo...'),
# ou uma por linha com a EPOCA no lugar do alvo ('Patata: entro la chiusura della
# fila'). Nenhuma das duas formas casa cultura com alvo no mesmo lugar, e por isso
# LEOPARD 5 EC e ACTIVUS 40 SC devolviam zero apesar de autorizarem dezenas de usos.
#
# A regra abaixo e a MESMA de pares_scope, so que le a lista explicita em vez da
# frase de titulo: exige herbicida E alvo INFESTANTI declarado no documento. Para
# fungicida ou inseticida ela nao dispara — ali o alvo e nominal e a lista de
# culturas nao diz qual doenca vale para qual cultura.
ABRE_LISTA_USOS = re.compile(
    r'usi\s+autorizzati|impiegat[oa]\s+nel\s+diserbo\s+delle\s+seguenti\s+colture|'
    r'pu[oò]\s+essere\s+impiegato\s+nel\s+diserbo|'
    r'viene\s+impiegato\s+per\s+il\s+diserbo\s+di|'
    r'nel\s+diserbo\s+delle\s+seguenti\s+colture|'
    r'infestanti\s+le\s+colture\s+di\s+seguito\s+riportate', re.I)


def pares_lista_de_usos(blocos, categoria_produto=None):
    herbicida = bool(categoria_produto and CATEGORIA_ERBICIDA.search(categoria_produto))
    if not herbicida:
        return []
    _c, target_scope, frases, _h = escopos(blocos, categoria_produto)
    if 'INFESTANTI' not in target_scope:
        return []
    abertura = None
    for b in sorted(blocos, key=lambda z: (z['page'], z['y0'])):
        if SECAO_PROIBIDA.search(b['text']):
            continue
        m = ABRE_LISTA_USOS.search(b['text'])
        if m:
            abertura = b['text'][m.start():m.start() + 700]
            break
    crops = set()
    if abertura:
        crops |= set(culturas_em(abertura))
        for g in expandir_grupos(abertura):
            crops |= set(g['MEMBROS'])
    # Cada cultura que ganha um paragrafo proprio de dose/epoca tambem esta autorizada:
    # 'Patata: entro la chiusura della fila' e uma linha de uso, mesmo sem alvo.
    # Nesta rota — e SO nesta — eu posso ser mais largo na leitura da cultura sem
    # arriscar par errado: o alvo ja esta fixado pelo documento inteiro (INFESTANTI de
    # herbicida), entao nao ha com o que cruzar. O unico risco e admitir cultura NAO
    # autorizada, e contra isso valem tres guardas: o bloco tem de ser curto, tem de
    # trazer marcador de uso ou de epoca, e nao pode trazer frase de exclusao (deriva,
    # cultura limitrofe, cultura sucessiva). A lista de infestantes fica de fora pelo
    # SECAO_PROIBIDA e pelo tamanho.
    EPOCA = re.compile(r'\bentro\b|\bfino\b|\bdalla?\b|\bpost-?emergenza\b|'
                       r'\bpre-?emergenza\b|\bpre-?trapianto\b|\bpost-?trapianto\b|'
                       r'\bpre-?semina\b|\bpre-?raccolta\b|stadio|chiusura\s+della\s+fila',
                       re.I)
    for b in blocos:
        t = b['text']
        if SECAO_PROIBIDA.search(t) or EXCLUSAO.search(t):
            continue
        if ESCOPO_ALVO_GLOBAL.search(t):
            continue          # este bloco lista MALERBAS, e nao culturas
        # A guarda vale por FRASE, e nao pelo bloco: num rotulo como ACTIVUS 40 SC
        # todas as declaracoes moram num bloco unico de dois mil caracteres, e cortar
        # pelo tamanho do bloco descartava as vinte e quatro autorizacoes de uma vez.
        for frase in re.split(r'(?<=[.;])\s+', t):
            if not (USO.search(frase) or EPOCA.search(frase)):
                continue
            if EXCLUSAO.search(frase) or ESCOPO_ALVO_GLOBAL.search(frase):
                continue
            crops |= set(culturas_em(frase))
            for g in expandir_grupos(frase):
                crops |= set(g['MEMBROS'])
    crops -= CULTURA_CATEGORIA
    return [{
        'CROP': c, 'TARGET': 'INFESTANTI', 'ROUTE': 'AUTHORISED_USE_LIST',
        'RELATION': 'SUPPORTED_PAIR',
        'CROP_SCOPE_DECLARED': True, 'TARGET_DECLARED': True,
        'CROP_AS_WRITTEN': (abertura or 'linha de dose por cultura')[:110],
        'TARGET_AS_WRITTEN': ' | '.join(frases[-2:])[:200],
        'PAGE': 0, 'CROP_Y': [0, 0], 'TARGET_Y': [0, 0],
    } for c in sorted(crops)]


def pares_scope(blocos, categoria_produto=None):
    crop_scope, target_scope, frases, herbicida = escopos(blocos, categoria_produto)
    if not crop_scope or not target_scope:
        return []
    pares = []
    for c in sorted(crop_scope):
        for t in sorted(target_scope):
            # SO o herbicida contra INFESTANTI e afirmavel por combinacao de escopo:
            # ali o rotulo inteiro tem um unico alvo de classe, e a lista de culturas
            # e a autorizacao. Qualquer outra combinacao fica como SCOPE_COMBINATION,
            # que NAO entra no conjunto publicado.
            firme = herbicida and t == 'INFESTANTI'
            pares.append({
                'CROP': c, 'TARGET': t, 'ROUTE': 'SCOPE_COMBINATION',
                'RELATION': 'SUPPORTED_PAIR' if firme else 'SCOPE_COMBINATION',
                'CROP_SCOPE_DECLARED': True, 'TARGET_DECLARED': True,
                'CROP_AS_WRITTEN': (frases[0] if frases else '')[:110],
                'TARGET_AS_WRITTEN': ' | '.join(frases[-2:])[:200],
                'PAGE': 0, 'CROP_Y': [0, 0], 'TARGET_Y': [0, 0],
            })
    return pares


# ── API ───────────────────────────────────────────────────────────────────────
def parse(pdf_path, rid, produto=None, ai=None, cache_dir=None, categoria=None):
    fonte = geometria_de(rid, pdf_path, cache_dir)
    if not fonte:
        return []
    blocos = ler_geometria(fonte)
    brutos = (pares_geometricos(blocos) + pares_inline(blocos)
              + pares_header_continuation(blocos)
              + pares_lista_de_usos(blocos, categoria)
              + pares_scope(blocos, categoria))
    # Um mesmo par pode sair pelas duas rotas ou de duas linhas. Fica a leitura mais
    # firme: afirmacao > duvida > exclusao. Guardar as tres seria contar a mesma
    # evidencia varias vezes.
    ordem = {'SUPPORTED_PAIR': 0, 'AMBIGUOUS_ROW': 1, 'SCOPE_COMBINATION': 2,
             'CROP_SCOPE_DECLARED': 3, 'EXCLUDED_PAIR': 4}
    brutos.sort(key=lambda p: ordem.get(p['RELATION'], 9))
    # FIX-A, num lugar so. Alvo de CATEGORIA nunca sai como par publicado: ele diz o
    # TIPO de inimigo, e nao o inimigo. Nao jogo fora — reclassifico para
    # CROP_SCOPE_DECLARED, que e o nivel 1 do item 5 e nao entra no conjunto.
    for p in brutos:
        if p['CROP'] in CULTURA_CATEGORIA and p['RELATION'] == 'SUPPORTED_PAIR':
            p['RELATION'] = 'CROP_SCOPE_DECLARED'
            p['WHY_NOT_PAIR'] = ('"%s" e grupo de culturas. Vale para os membros que o '
                                 'rotulo enumerar, e nao como cultura propria.'
                                 % p['CROP'])
        if p['TARGET'] in ALVO_CATEGORIA and p['RELATION'] == 'SUPPORTED_PAIR':
            p['RELATION'] = 'CROP_SCOPE_DECLARED'
            p['WHY_NOT_PAIR'] = ('"%s" e categoria de inimigo, nao inimigo. A frase '
                                 'declara escopo de cultura.' % p['TARGET'])
    vistos, saida = set(), []
    for p in brutos:
        k = (p['CROP'], p['TARGET'])
        if k in vistos:
            continue
        vistos.add(k)
        st, nota = status_taxonomico(p['TARGET_AS_WRITTEN'])
        norm = normalizar_substancia(p['TARGET_AS_WRITTEN'])
        p.update({
            'REGISTRATION_ID': rid, 'PRODUCT': produto, 'ACTIVE_INGREDIENTS': ai,
            'TAXONOMIC_STATUS': st, 'TAXONOMIC_NOTE': nota,
            'SUBSTANCE_NORMALISATION': norm,
            'PROVENANCE': 'MINISTERO_LABEL_PDF · %s · p%d y%s' % (rid, p['PAGE'],
                                                                 p['TARGET_Y']),
            'PARSER_VERSION': PARSER_VERSION,
        })
        saida.append(p)
    return saida


if __name__ == '__main__':
    rid = sys.argv[1]
    d = sys.argv[2] if len(sys.argv) > 2 else '.'
    for p in parse(os.path.join(d, '%s.pdf' % rid), rid, cache_dir=d):
        print('%-14s %-18s %-16s %s' % (p['CROP'], p['TARGET'], p['RELATION'],
                                        p['TARGET_AS_WRITTEN'][:60]))
