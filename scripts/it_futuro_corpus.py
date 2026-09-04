#!/usr/bin/env python3
"""Monta o CORPUS da coleta nova e varre candidatos a sinal FUTURO.

Duas coisas separadas, de proposito:

  1. o corpus — todo texto coletado nesta missao que esta VERSIONADO, com
     SOURCE_ID, SOURCE_TYPE e SOURCE_DATE. O que morreu com o conteiner nao entra:
     varrer o que nao existe mais produziria censo mentiroso.

  2. os CANDIDATOS — trechos onde a lingua marca futuro. Candidato nao e sinal.
     A missao e explicita: "a expressao textual e apenas candidato; a classificacao
     final precisa ser sustentada pelo contexto". Este arquivo entrega candidatos
     ordenados; quem decide o EVIDENCE_TIME_STATE sou eu, lendo.
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')

# ── lexico de futuro, em italiano ────────────────────────────────────────────
# Cada entrada traz o TIPO que a expressao SUGERE. Sugere, nao decide: 'previsione'
# tanto abre uma previsao meteorologica quanto fecha a frase 'contrariamente alla
# previsione, non e successo'. O tipo final sai da leitura.
LEXICO = [
    ('prossim[ao]\\s+(?:campagna|stagione|annata|primavera|estate|autunno|inverno)',
     'PROXIMA_CAMPANHA'),
    ('nell[ea]\\s+prossim[ei]\\s+(?:settimane|giorni|mesi|anni)', 'PROXIMAS_SEMANAS'),
    ('prossim[oi]\\s+(?:ciclo|cicli|anno|anni|mese|mesi)', 'PROXIMO_CICLO'),
    ('pre-?\\s?raccolta|prima\\s+della\\s+raccolta', 'PRE_COLHEITA'),
    ('prevision[ei]|si\\s+prevede|e\\s+previsto|sono\\s+previst[ei]|previst[oaei]\\b',
     'PREVISAO'),
    ('attes[oaei]\\b|ci\\s+si\\s+attende|ci\\s+aspettiamo|aspettarsi', 'ESPERADO'),
    ('tendenza|trend\\b|in\\s+aumento|in\\s+crescita|in\\s+diminuzione|in\\s+calo',
     'TENDENCIA'),
    ('dovr[àa]\\b|dovrebbe(?:ro)?\\b|potr[àa]\\b|potrebbe(?:ro)?\\b|sar[àa]\\b|'
     'saranno\\b|avremo\\b|vedremo\\b', 'MODAL_FUTURO'),
    ('aument(?:o|er[àa]|eranno|ando)|riduzion[ei]|ridurr|diminuir|incremento',
     'AUMENTO_REDUCAO'),
    ('nuov[ao]\\s+(?:raccomandazione|indicazione|linea\\s+guida|protocollo|strategia)',
     'NOVA_RECOMENDACAO'),
    ('resistenz[ae]', 'RESISTENCIA'),
    ('nuov[ao]\\s+autorizzazione|autorizzazione\\s+(?:di\\s+)?emergenza|'
     'deroga|articolo\\s+53', 'NOVA_AUTORIZACAO'),
    ('revoc(?:a|ato|ata|he)|ritir(?:o|ato|ata)|non\\s+pi[uù]\\s+(?:disponibile|'
     'utilizzabile|autorizzat)|elimin(?:azione|ato)\\s+(?:della|del)\\s+sostanza',
     'RETIRADA'),
    ('lancio|immission[ei]\\s+(?:in|sul)\\s+(?:commercio|mercato)|nuovo\\s+prodotto|'
     'sar[àa]\\s+disponibile', 'LANCAMENTO'),
    ('entra\\s+in\\s+vigore|a\\s+partire\\s+dal|dal\\s+1[°º]?\\s+(?:gennaio|luglio)|'
     'entro\\s+il\\s+\\d{4}|scadenz[ae]|scade\\s+(?:il|nel)|regolamento\\s+\\(UE\\)|'
     'direttiva|normativ[ae]\\s+(?:nuova|europea)', 'MUDANCA_NORMATIVA'),
    ('convegno|congresso|giornata\\s+tecnica|workshop|seminario|prossimo\\s+incontro',
     'EVENTO_TECNICO'),
    ('sperimentazion[ei]|prova\\s+di\\s+campo|prove\\s+in\\s+corso|studio\\s+in\\s+corso|'
     'stiamo\\s+studiando|ricerca\\s+in\\s+corso', 'PESQUISA_EM_CURSO'),
    ('cambiamento\\s+climatico|riscaldamento|annata\\s+(?:calda|piovosa|siccitosa)|'
     'siccit[àa]|piogge\\s+(?:attese|previste)', 'CLIMA'),
    ('soglia\\s+(?:di\\s+)?intervento|monitoraggio|trappol[ae]|catture', 'MONITORAMENTO'),
]
LEXICO_RX = [(re.compile(p, re.I), t) for p, t in LEXICO]

# marcas de dominio: sem cultura, alvo ou regiao o candidato quase nunca vira sinal
CROP_RX = re.compile(
    r'\b(vite|vigneto|uva|olivo|oliv[eo]|melo|mel[ea]\b|pero|pere\b|pesco|pesch[ae]|'
    r'albicocc|ciliegi|susin|nocciol|noce|noci\b|mandorl|castagn|agrum|arancio|limone|'
    r'clementin|pomodor|patata|patate|barbabietola|frumento|grano\b|orzo|mais|riso\b|'
    r'soia|girasole|colza|cipolla|aglio|carota|lattuga|cavol|carciofo|fragol|melone|'
    r'cocomer|zucchin|cetriol|peperone|melanzana|fagiol|pisell|tabacco|erba\s+medica|'
    r'kiwi|actinidia|sorgo|segale|triticale|avena)\b', re.I)
ISSUE_RX = re.compile(
    r'\b(peronospor|oidio|botrite|botrytis|muffa\s+grigia|ticchiolatur|monili|'
    r'antracnos|alternari|septori|ruggine|ruggini|fusarios|cercospor|elmintosporios|'
    r'rincosporios|ramulari|carbone|carie|flavescenz|scaphoideus|cicalin|afid|'
    r'cimice|halyomorpha|carpocaps|cydia|tignol|anarsia|tripid|acar|ragnetto|'
    r'dorifora|elaterid|piralide|ostrinia|diabrotica|nottue|spodoptera|mosca\s+'
    r'(?:olearia|della\s+frutta)|bactrocera|ceratitis|drosophila|suzukii|xylella|'
    r'psilla|cocciniglia|aleurodid|nematod|repilo|occhio\s+di\s+pavone|lebbra|'
    r'rogna|verticilli|infestanti|malerbe|graminacee|dicotiledoni)\b', re.I)
REGION_RX = re.compile(
    r'\b(Veneto|Lombardia|Piemonte|Emilia[- ]Romagna|Toscana|Puglia|Sicilia|Sardegna|'
    r'Campania|Calabria|Basilicata|Molise|Abruzzo|Marche|Umbria|Lazio|Liguria|'
    r'Friuli|Trentino|Alto\s+Adige|Valle\s+d.?Aosta|Romagna|Veronese|Trevigiano)\b')
DATE_RX = re.compile(
    r'\b(20(?:2[5-9]|3[0-5]))\b|\b(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|'
    r'agosto|settembre|ottobre|novembre|dicembre)\b', re.I)


def _falas():
    """Transcricoes VERSIONADAS. As que morreram no conteiner nao entram."""
    for f in sorted(glob.glob(os.path.join(SAMPLES, '**', 'falas', '*.json'),
                              recursive=True)):
        d = json.load(open(f, encoding='utf-8'))
        txt = d.get('TRANSCRIPT') or ''
        if len(txt) < 400:
            continue
        yield {
            'SOURCE_ID': d.get('EXTERNAL_ID') or os.path.basename(f)[:-5],
            'SOURCE_TYPE': 'VIDEO_CONVEGNO_TRANSCRICAO',
            'SOURCE_DATE': d.get('PUBLICATION_DATE') or 'UNKNOWN',
            'TITLE': d.get('TITLE') or '',
            'ORG': d.get('CHANNEL_NAME') or d.get('ORGANISATION') or '',
            'URL': d.get('URL') or '',
            'PATH': os.path.relpath(f, ROOT),
            'TEXT': txt,
        }


def _campo():
    for nome in ('IT-CAMPO-SINAIS-VERIFICADOS-V2.json',
                 'IT-CAMPO-SINAIS-VERIFICADOS-V1.json'):
        p = os.path.join(SAMPLES, 'IT-CAMPO-V1', nome)
        if not os.path.exists(p):
            continue
        for s in json.load(open(p, encoding='utf-8')).get('SIGNALS', []):
            yield {
                'SOURCE_ID': 'CAMPO:%s' % (s.get('source_url') or '')[-11:],
                'SOURCE_TYPE': 'SINAL_DE_CAMPO_VERIFICADO',
                'SOURCE_DATE': s.get('publication_date') or 'UNKNOWN',
                'TITLE': s.get('title') or '',
                'ORG': s.get('channel_name') or '',
                'URL': s.get('source_url') or '',
                'PATH': 'data/samples/IT-CAMPO-V1/%s' % nome,
                'TEXT': ' '.join(str(s.get(k) or '') for k in
                                 ('quote_it', 'crop', 'issue', 'region',
                                  'adama_relation', 'proves', 'does_not_prove')),
                'STRUCT': s,
            }


def _audio():
    p = os.path.join(SAMPLES, 'IT-VOZ-AUDIO-V2', 'IT-VOZ-AUDIO-TRANSCRICOES-V2.json')
    if not os.path.exists(p):
        return
    for r in json.load(open(p, encoding='utf-8')).get('RECORDS', []):
        txt = ' '.join(str(r.get(k) or '') for k in
                       ('TITLE', 'DESCRIPTION', 'TRANSCRIPT', 'ADAMA_RELEVANCE_REASON'))
        if len(txt) < 200:
            continue
        yield {'SOURCE_ID': r.get('EXTERNAL_ID') or r.get('SHOW_ID') or 'AUDIO',
               'SOURCE_TYPE': 'AUDIO_PODCAST',
               'SOURCE_DATE': r.get('PUBLICATION_DATE') or 'UNKNOWN',
               'TITLE': r.get('TITLE') or '', 'ORG': r.get('ORIGIN') or '',
               'URL': r.get('AUDIO_URL') or '',
               'PATH': 'data/samples/IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json',
               'TEXT': txt}


def _instagram():
    for v in ('V3', 'V2', 'V1'):
        p = os.path.join(SAMPLES, 'IT-INSTAGRAM-%s' % v,
                         'IT-INSTAGRAM-TRANSCRICOES-%s.json' % v)
        if not os.path.exists(p):
            continue
        for r in json.load(open(p, encoding='utf-8')).get('ITEMS', []):
            txt = ' '.join(str(r.get(k) or '') for k in ('CAPTION', 'TRANSCRIPT'))
            if len(txt) < 200:
                continue
            yield {'SOURCE_ID': 'IG:%s' % r.get('SHORTCODE'),
                   'SOURCE_TYPE': 'INSTAGRAM_CREATOR',
                   'SOURCE_DATE': r.get('PUBLICATION_DATE') or 'UNKNOWN',
                   'TITLE': (r.get('CAPTION') or '')[:90],
                   'ORG': r.get('ORGANISATION') or r.get('HANDLE') or '',
                   'URL': r.get('URL') or '',
                   'PATH': os.path.relpath(p, ROOT), 'TEXT': txt}


def _bollettini():
    p = os.path.join(SAMPLES, 'IT-CAMPO-V1', 'IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json')
    if not os.path.exists(p):
        return
    # O arquivo guarda 421 HITS de substancia ativa dentro dos boletins, cada um com
    # DATE, AREA e o CONTEXTO da frase. Agrupo por (data, area): a unidade de leitura
    # e o boletim, e nao a ocorrencia isolada da molecula.
    d = json.load(open(p, encoding='utf-8'))
    por_bol = {}
    for h in d.get('HITS', []):
        k = (h.get('DATE'), h.get('AREA'))
        por_bol.setdefault(k, []).append(h)
    for (data, area), hs in sorted(por_bol.items(), key=lambda z: str(z[0])):
        txt = ' '.join(str(h.get('CTX') or '') for h in hs)
        if len(txt) < 120:
            continue
        yield {'SOURCE_ID': 'BOLL-ER:%s:%s' % (data, area),
               'SOURCE_TYPE': 'BOLLETTINO_REGIONALE',
               'SOURCE_DATE': data or 'UNKNOWN',
               'TITLE': 'Bollettino di produzione integrata Emilia-Romagna — %s' % area,
               'ORG': 'Regione Emilia-Romagna', 'URL': '',
               'PATH': os.path.relpath(p, ROOT),
               'TEXT': txt,
               'SUBSTANCIAS': sorted({h.get('AI') for h in hs if h.get('AI')})}


def corpus():
    vistos = set()
    for gen in (_falas, _campo, _audio, _instagram, _bollettini):
        for d in gen():
            k = (d['SOURCE_ID'], d['SOURCE_TYPE'])
            if k in vistos:
                continue
            vistos.add(k)
            yield d


def frases(txt):
    """ASR nao pontua bem. Corto por pontuacao E por tamanho, para a janela nao
    virar um paragrafo inteiro onde qualquer coisa 'aparece perto' de qualquer coisa."""
    for bruto in re.split(r'(?<=[.!?;])\s+|\n+', txt):
        bruto = bruto.strip()
        while len(bruto) > 420:
            corte = bruto.rfind(' ', 0, 420)
            yield bruto[:corte if corte > 200 else 420]
            bruto = bruto[corte if corte > 200 else 420:].strip()
        if len(bruto) > 15:
            yield bruto


def candidatos():
    for d in corpus():
        fs = list(frases(d['TEXT']))
        for i, f in enumerate(fs):
            tipos = sorted({t for rx, t in LEXICO_RX if rx.search(f)})
            if not tipos:
                continue
            # a janela e a frase mais uma vizinha de cada lado: o contexto que
            # sustenta ou derruba a leitura de futuro mora ali.
            jan = ' '.join(fs[max(0, i - 1):i + 2])
            crops = sorted({m.group(0).lower() for m in CROP_RX.finditer(jan)})
            issues = sorted({m.group(0).lower() for m in ISSUE_RX.finditer(jan)})
            regs = sorted({m.group(0) for m in REGION_RX.finditer(jan)})
            datas = sorted({m.group(0) for m in DATE_RX.finditer(jan)})
            yield {
                **{k: v for k, v in d.items() if k not in ('TEXT', 'STRUCT')},
                'IDX': i, 'TIPOS_SUGERIDOS': tipos,
                'FRASE': f, 'JANELA': jan,
                'CROPS': crops, 'ISSUES': issues, 'REGIONS': regs, 'DATAS': datas,
                'PESO': (len(tipos) + 2 * bool(crops) + 2 * bool(issues)
                         + bool(regs) + bool(datas)),
            }


if __name__ == '__main__':
    import collections
    import sys
    cs = list(candidatos())
    docs = list(corpus())
    print('DOCUMENTOS_NO_CORPUS = %d' % len(docs))
    print('CHARS_NO_CORPUS      = %d' % sum(len(d['TEXT']) for d in docs))
    print('CANDIDATOS_BRUTOS    = %d' % len(cs))
    print('  com cultura E alvo = %d' % sum(1 for c in cs if c['CROPS'] and c['ISSUES']))
    print()
    print('por SOURCE_TYPE:')
    for k, v in collections.Counter(d['SOURCE_TYPE'] for d in docs).most_common():
        print('  %-32s %d' % (k, v))
    print()
    print('candidatos por TIPO sugerido:')
    tt = collections.Counter(t for c in cs for t in c['TIPOS_SUGERIDOS'])
    for k, v in tt.most_common():
        print('  %-24s %d' % (k, v))
    if len(sys.argv) > 1:
        json.dump(cs, open(sys.argv[1], 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
