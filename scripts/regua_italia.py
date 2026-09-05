#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RÉGUA ITÁLIA · FITOSSANITÁRIO E DANINHAS — implementa `docs/regras/REGUA-ITALIA-FITOSSANITARIA.md`.

    python3 scripts/regua_italia.py

HERANÇA DECLARADA
------------------
O contrato é portado de `portal-sintonia/REGUA-MISSAO-5-FITOSSANITARIO.md` (Brasil,
23/08/2026). As quatro leis que mais mudam o resultado, e que eu teria errado sozinho:

    A UNIDADE É O PAR         cultura × alvo, nunca o documento e nunca a fonte
    TRÊS VEREDITOS           PASSA · NÃO SEI · BARRA — «não sei» jamais vira «barra»
    O PAR É INFERIDO         cultura e alvo são observados cada um; a LIGAÇÃO é nossa
    COMENTÁRIO É PLATEIA     o canal do comentário é o CANAL, nunca o autor

E a que salva do erro mais fácil de todos:

    CONTAGEM BRUTA NÃO É SINAL DE ALTA. Só PROPORÇÃO, e só entre janelas comparáveis.

O QUE É NOVO AQUI, E POR QUE PRECISOU NASCER
---------------------------------------------
A quarentena. A brasileira tinha de resolver `ferrugem` (doença vs. metal) e `acaro`
(lavoura vs. poeira). A italiana tem tudo isso E MAIS a colisão entre línguas, porque a
mesma busca devolveu itálico, espanhol, francês e inglês no mesmo saco:

    vite   videira · PARAFUSO            (colisão dentro do italiano)
    riso   arroz · riso de rir           (colisão dentro do italiano)
    mais   milho · «mas» francês         (colisão entre línguas)
    pero   pereira · «porém» espanhol    (colisão entre línguas)
    grano  trigo italiano · grão espanhol (colisão entre línguas)

Por isso todo termo em quarentena exige ÂNCORA agrícola no mesmo texto, e o item ainda
precisa passar por um teste de LÍNGUA — medido por palavra funcional, nunca herdado do
`CASE_ID`, porque `CASE_ID` diz de que CONSULTA o item veio, não em que língua ele está.

    A ÂNCORA REDUZ A SUJEIRA. NÃO A ELIMINA. Risco residual fica DECLARADO.
"""
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSOR = os.path.join(ROOT, 'data', 'samples', 'SENSOR-PILOT')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-REGUA')

MIN_DOCS_PAR = 3          # abaixo disto o par não recebe posição
MIN_FONTES_SOBE = 2       # abaixo disto o par nunca sai do NÍVEL 1
MIN_TEXTO = 40            # texto curto demais não sustenta par


try:
    from sensor_medir import plateia_do_canal as _pdc
except Exception:
    _pdc = None


def _plateia(canal):
    """A plateia do canal viaja com o VÍDEO, não só com o comentário.

    Um vídeo de canal de horta doméstica é conversa de jardim tanto quanto o
    comentário embaixo dele. Medir a plateia só na plateia era medir metade."""
    if _pdc is None:
        return 'NOT_KNOWN'
    return _pdc(canal)[0]


def _veredito_plateia(c):
    """Em UMA palavra: de que mundo vem a evidência deste par.

    Nasceu de um erro que quase passou: POMODORO x PERONOSPORA tinha 29
    documentos e 15 fontes — parecia o terceiro par mais forte do corpus. Ao
    separar a plateia, 15 evidências vinham de canal de horta doméstica e 1 de
    canal profissional. É tomate de vaso, não tomate industrial.

        SOMAR AS DUAS PLATEIAS PRODUZ UM NÚMERO QUE NÃO DESCREVE NENHUM MUNDO.
    """
    pr = c.get('PROFESSIONAL_FIELD_AUDIENCE', 0)
    ho = c.get('HOBBY_GARDEN_AUDIENCE', 0)
    if pr == 0 and ho == 0:
        return 'NAO_SEI'
    if ho == 0:
        return 'SUSTENTADO_POR_CANAL_PROFISSIONAL'
    if pr == 0:
        return 'SUSTENTADO_SO_POR_HORTA_DOMESTICA'
    if pr >= ho * 2:
        return 'PREDOMINANTEMENTE_PROFISSIONAL'
    if ho >= pr * 2:
        return 'PREDOMINANTEMENTE_HORTA_DOMESTICA'
    return 'MISTO'


def _n(t):
    """Sem acento, minúsculo. A borda de palavra vem depois, no regex."""
    return ''.join(c for c in unicodedata.normalize('NFD', t or '')
                   if unicodedata.category(c) != 'Mn').lower()


# ── ÂNCORA AGRÍCOLA ─────────────────────────────────────────────────────────────
# Não é «fala de agricultura». É: há UMA palavra que só aparece em texto de lavoura.
ANCORA = re.compile(
    r'\b(ettar|coltur|coltiv|semin|raccolt|diserb|infestant|malerb|fitosanitar|'
    r'trattament|irrorazion|ugell|dose|litri per ettaro|principio attivo|'
    r'erbicid|fungicid|insetticid|agronom|azienda agricol|campo|terreno|'
    r'vigneto|frutteto|risaia|granella|spiga|fioritura|emergenza|pre-emergenza|'
    r'post-emergenza|varieta|ibrid|concim|aratur|sarchiatur)')

# ── LÍNGUA, por palavra funcional. NUNCA herdada do CASE_ID. ────────────────────
LINGUA = {
    'it': re.compile(r'\b(che|non|per|con|della|delle|nel|nella|sono|come|piu|'
                     r'anche|questo|questa|gli|dei|degli|una|uno)\b'),
    'es': re.compile(r'\b(que|los|las|para|con|del|una|como|pero|muy|este|esta|'
                     r'hay|son|mas)\b'),
    'fr': re.compile(r'\b(que|les|des|pour|avec|dans|une|comme|cette|sont|plus|'
                     r'nous|vous|est)\b'),
    'en': re.compile(r'\b(the|and|for|with|that|this|from|have|are|you|your|'
                     r'about|will)\b'),
}


def lingua_de(texto):
    """→ (lingua, evidencia). Empate ou pouco sinal = NÃO SEI, nunca chute."""
    t = _n(texto)
    pont = {k: len(v.findall(t)) for k, v in LINGUA.items()}
    top = sorted(pont.items(), key=lambda kv: -kv[1])
    if not top or top[0][1] < 3:
        return 'NAO_SEI', 'menos de 3 marcadores funcionais'
    if len(top) > 1 and top[0][1] == top[1][1]:
        return 'NAO_SEI', 'empate entre %s e %s' % (top[0][0], top[1][0])
    return top[0][0], '%d marcadores de %s' % (top[0][1], top[0][0])


# ── CULTURAS ────────────────────────────────────────────────────────────────────
# (chave, regex, EXIGE_ANCORA). O terceiro campo é a quarentena, item a item.
CULTURAS = [
    ('VITE',        r'\b(vite|viti|vigneto|vigneti|vitigno|vitigni|uva|viticoltur)', True),
    ('MAIS',        r'\b(mais|granoturco|granturco)\b', True),
    ('FRUMENTO',    r'\b(frumento|grano duro|grano tenero|triticum|cerealicol)', False),
    ('GRANO_GEN',   r'\b(grano|grani)\b', True),
    ('ORZO',        r'\b(orzo)\b', False),
    ('SOIA',        r'\b(soia)\b', False),
    ('RISO',        r'\b(riso|risaia|risaie|risicol)', True),
    ('BARBABIETOLA', r'\b(barbabietola|bietola|bietole)', False),
    ('POMODORO',    r'\b(pomodoro|pomodori)', False),
    ('MELO',        r'\b(melo|meli|melicoltur|pomacee)', False),
    ('PERO',        r'\b(pero|peri)\b', True),
    ('OLIVO',       r'\b(olivo|olivi|oliveto|olivicoltur|olivicol)', False),
    ('GIRASOLE',    r'\b(girasole|girasoli)', False),
    ('PATATA',      r'\b(patata|patate)', False),
    ('COLZA',       r'\b(colza)\b', False),
    ('ERBA_MEDICA', r'\b(erba medica)', False),
    ('SORGO',       r'\b(sorgo)\b', False),
    ('AGRUMI',      r'\b(agrumi|arancio|limone)', False),
    ('PESCO',       r'\b(pesco|pescheto)', False),
    ('ORTICOLE',    r'\b(orticol|ortaggi)', False),
]

# ── ALVOS ───────────────────────────────────────────────────────────────────────
# (chave, regex, CATEGORIA, EXIGE_ANCORA)
ALVOS = [
    ('PERONOSPORA',    r'\b(peronospora|plasmopara viticola)', 'FUNGICIDA', False),
    ('OIDIO',          r'\b(oidio|erysiphe necator|mal bianco)', 'FUNGICIDA', False),
    ('BOTRITE',        r'\b(botrite|botrytis|muffa grigia)', 'FUNGICIDA', False),
    ('SEPTORIOSI',     r'\b(septorios|zymoseptoria|septoria)', 'FUNGICIDA', False),
    ('FUSARIOSI',      r'\b(fusarios|fusarium)', 'FUNGICIDA', False),
    ('TICCHIOLATURA',  r'\b(ticchiolatura|venturia inaequalis)', 'FUNGICIDA', False),
    ('RUGGINE',        r'\b(ruggine|puccinia)', 'FUNGICIDA', True),
    ('CERCOSPORA',     r'\b(cercospor)', 'FUNGICIDA', False),
    ('BRUSONE',        r'\b(brusone|pyricularia|magnaporthe)', 'FUNGICIDA', False),
    ('ELMINTOSPORIOSI', r'\b(elmintosporios|helminthosporium)', 'FUNGICIDA', False),
    ('MARCIUME',       r'\b(black rot|marciume nero|marciume acido)', 'FUNGICIDA', False),
    ('SCAFOIDEO',      r'\b(scaphoideus|scafoideo)', 'INSETICIDA', False),
    ('CICALINA_GEN',   r'\b(cicalin)', 'INSETICIDA', True),
    ('PIRALIDE',       r'\b(piralide|ostrinia)', 'INSETICIDA', False),
    ('DIABROTICA',     r'\b(diabrotica)', 'INSETICIDA', False),
    ('AFIDI',          r'\b(afide|afidi|aphis|myzus)', 'INSETICIDA', False),
    ('ELATERIDI',      r'\b(elateridi|agriotes|ferretti)', 'INSETICIDA', True),
    ('NOTTUA',         r'\b(nottua|nottue|agrotis)', 'INSETICIDA', True),
    ('CIMICE',         r'\b(cimice asiatica|halyomorpha)', 'INSETICIDA', False),
    ('CARPOCAPSA',     r'\b(carpocapsa|cydia pomonella)', 'INSETICIDA', False),
    ('MOSCA_OLIVO',    r'\b(mosca dell.olivo|bactrocera oleae)', 'INSETICIDA', False),
    ('CERATITIS',      r'\b(ceratitis|mosca della frutta)', 'INSETICIDA', False),
    ('RAGNETTO',       r'\b(ragnetto rosso|tetranychus)', 'ACARICIDA', False),
    ('ACARO_GEN',      r'\b(acaro|acari)\b', 'ACARICIDA', True),
    ('FLAVESCENZA',    r'\b(flavescenza|giallumi)', 'FITOPLASMA', False),
    ('NEMATODI',       r'\b(nematod|meloidogyne)', 'NEMATICIDA', False),
    # ── daninhas nomeadas ──
    ('AMARANTO',       r'\b(amaranto|amaranthus)', 'HERBICIDA', False),
    ('GIAVONE',        r'\b(giavone|giavoni|echinochloa)', 'HERBICIDA', False),
    ('RISO_CRODO',     r'\b(riso crodo)', 'HERBICIDA', False),
    ('LOIETTO',        r'\b(loietto|loglio|lolium)', 'HERBICIDA', False),
    ('AVENA_SELVATICA', r'\b(avena sterilis|avena selvatica|avena fatua)', 'HERBICIDA', False),
    ('PAPAVERO',       r'\b(papavero|papaver)', 'HERBICIDA', False),
    ('SORGHETTA',      r'\b(sorghetta|sorghum halepense)', 'HERBICIDA', False),
    ('ABUTILON',       r'\b(abutilon|cencio molle)', 'HERBICIDA', False),
    ('CHENOPODIO',     r'\b(chenopodio|chenopodium|farinello)', 'HERBICIDA', False),
    ('SOLANO',         r'\b(solanum nigrum|erba morella)', 'HERBICIDA', False),
    ('CONVOLVOLO',     r'\b(convolvolo|fallopia|poligono)', 'HERBICIDA', False),
    ('SETARIA_PANICO', r'\b(setaria|panico|digitaria)', 'HERBICIDA', False),
    ('CIPERO',         r'\b(cipero|cyperus)', 'HERBICIDA', False),
    ('PORTULACA',      r'\b(portulaca)', 'HERBICIDA', False),
]

# ── EIXOS PRÓPRIOS · não são alvo, e nunca entram ao lado de um organismo ───────
ASSUNTOS = [
    ('ASSUNTO_DISERBO',     r'\b(diserbo|diserbant|infestant|malerb)', 'HERBICIDA'),
    ('ASSUNTO_MICOTOSSINA', r'\b(micotossin|deossinivalenolo|aflatossin|fumonisin)',
     'QUALIDADE_GRANELLA'),
    ('ASSUNTO_RESISTENZA',  r'\b(resistenz)', 'AFIRMACAO_SOBRE_RESISTENCIA'),
]

CULT_RX = [(k, re.compile(rx), anc) for k, rx, anc in CULTURAS]
ALVO_RX = [(k, re.compile(rx), cat, anc) for k, rx, cat, anc in ALVOS]
ASSU_RX = [(k, re.compile(rx), cat) for k, rx, cat in ASSUNTOS]


def _casar(texto, tabela, tem_ancora):
    """→ [(chave, termo_casado, extra...)]. Quarentena barra sem âncora."""
    fora = []
    for item in tabela:
        chave, rx = item[0], item[1]
        exige = item[-1] if isinstance(item[-1], bool) else False
        m = rx.search(texto)
        if not m:
            continue
        if exige and not tem_ancora:
            continue                       # QUARENTENA: casou, mas sem âncora → BARRA
        fora.append((chave, m.group(0), item))
    return fora


def trecho_que_casou(texto_original, termo, janela=110):
    """O pedaço que casou, não o documento inteiro. Herdado do `radar-do-campo`."""
    t = _n(texto_original)
    i = t.find(_n(termo))
    if i < 0:
        return None
    a = max(0, i - janela)
    b = min(len(texto_original), i + len(termo) + janela)
    return ('…' if a > 0 else '') + texto_original[a:b].replace('\n', ' ').strip() + \
           ('…' if b < len(texto_original) else '')


def _docs():
    """Todo documento do acervo de sensores, com sua PORTA NATIVA."""
    med = json.load(open(os.path.join(SENSOR, 'MEDICAO.json'), encoding='utf-8'))
    for v in med['VIDEOS_ITEMS']:
        texto = ' '.join(str(v.get(k) or '') for k in ('TITLE', 'DESCRIPTION'))
        yield {
            'AUDIENCE': _plateia(v.get('CHANNEL')),
            'DOC_ID': 'YT-VID-%s' % v.get('EXTERNAL_ID'),
            'PORTA': 'youtube+video_metadata',
            'TEXTO': texto,
            'CANAL': v.get('CHANNEL'),
            'CANAL_IDENTIDADE': v.get('CHANNEL_IDENTITY_STATE') or 'NOT_PROVED',
            'URL': v.get('SOURCE_URL'),
            'DATA_EVIDENCIA': v.get('PUBLISHED_AT'),
            'CAMADA': 'FONTE',
            'ATRIBUIBILIDADE': ('IDENTIFICADA'
                                if v.get('CHANNEL_IDENTITY_STATE') == 'PROVED'
                                else 'NAO_ATRIBUIVEL'),
            'CASE_ID': v.get('CASE_ID'),
        }
        if v.get('TRANSCRIPT'):
            yield {
                'AUDIENCE': _plateia(v.get('CHANNEL')),
                'DOC_ID': 'YT-TRA-%s' % v.get('EXTERNAL_ID'),
                'PORTA': 'youtube+transcricao',
                'TEXTO': v['TRANSCRIPT'],
                'CANAL': v.get('CHANNEL'),
                'CANAL_IDENTIDADE': v.get('CHANNEL_IDENTITY_STATE') or 'NOT_PROVED',
                'URL': v.get('SOURCE_URL'),
                'DATA_EVIDENCIA': v.get('PUBLISHED_AT'),
                'CAMADA': 'FONTE',
                'ATRIBUIBILIDADE': ('IDENTIFICADA'
                                    if v.get('CHANNEL_IDENTITY_STATE') == 'PROVED'
                                    else 'NAO_ATRIBUIVEL'),
                'CASE_ID': v.get('CASE_ID'),
            }
    for c in med['COMMENTS_ITEMS']:
        yield {
            'AUDIENCE': c.get('CHANNEL_AUDIENCE_KIND') or 'NOT_KNOWN',
            'DOC_ID': 'YT-COM-%s' % c.get('COMMENT_ID'),
            'PORTA': 'youtube+comentario',
            'TEXTO': c.get('COMMENT_TEXT_RAW') or '',
            'CANAL': c.get('SOURCE_ENTITY'),
            'CANAL_IDENTIDADE': 'NOT_APPLICABLE',
            'URL': c.get('SOURCE_URL'),
            # O comentário devolve tempo RELATIVO. Converter inventaria precisão.
            'DATA_EVIDENCIA': None,
            'CAMADA': 'PLATEIA',
            'ATRIBUIBILIDADE': 'NAO_ATRIBUIVEL',
            'CASE_ID': c.get('CASE_ID'),
        }


def medir():
    pares = defaultdict(lambda: {'EVIDENCIAS': [], 'PORTAS': set(), 'FONTES': set(),
                                 'CAMADAS': Counter(), 'CATEGORIAS': set(),
                                 'PLATEIAS': Counter(), 'RECORTES': Counter()})
    assuntos = defaultdict(lambda: {'N': 0, 'PORTAS': set(), 'FONTES': set()})
    total = barrados = curtos = sem_lingua = 0
    quarentena_barrou = Counter()
    lingua_conta = Counter()

    for d in _docs():
        total += 1
        bruto = d['TEXTO'] or ''
        if len(bruto.strip()) < MIN_TEXTO:
            curtos += 1
            continue
        t = _n(bruto)
        tem_anc = bool(ANCORA.search(t))
        lin, lin_ev = lingua_de(bruto)
        lingua_conta[lin] += 1

        culturas = _casar(t, CULT_RX, tem_anc)
        alvos = _casar(t, ALVO_RX, tem_anc)

        # contabiliza o que a quarentena barrou, para a régua poder ser auditada
        for tabela, nome in ((CULT_RX, 'CULTURA'), (ALVO_RX, 'ALVO')):
            for item in tabela:
                exige = item[-1] if isinstance(item[-1], bool) else False
                if exige and not tem_anc and item[1].search(t):
                    quarentena_barrou['%s:%s' % (nome, item[0])] += 1

        # LÍNGUA: um texto que não é italiano não sustenta par italiano.
        if lin != 'it':
            if culturas and alvos:
                sem_lingua += 1
            continue

        for k, termo, _i in ASSU_RX and _casar(t, ASSU_RX, tem_anc):
            a = assuntos[k]
            a['N'] += 1
            a['PORTAS'].add(d['PORTA'])
            a['FONTES'].add(d['CANAL'])

        if not culturas or not alvos:
            barrados += 1
            continue

        for ck, ctermo, _c in culturas:
            for ak, atermo, aitem in alvos:
                p = pares[(ck, ak)]
                p['CATEGORIAS'].add(aitem[2])
                p['PORTAS'].add(d['PORTA'])
                p['FONTES'].add(d['CANAL'])
                p['CAMADAS'][d['CAMADA']] += 1
                p['PLATEIAS'][d.get('AUDIENCE') or 'NOT_APPLICABLE'] += 1
                p['RECORTES'][d.get('CASE_ID') or 'NAO_SEI'] += 1
                if len(p['EVIDENCIAS']) < 12:
                    p['EVIDENCIAS'].append({
                        'DOC_ID': d['DOC_ID'], 'PORTA': d['PORTA'],
                        'CANAL': d['CANAL'], 'URL': d['URL'],
                        'DATA_EVIDENCIA': d['DATA_EVIDENCIA'] or 'NAO_SEI',
                        'ATRIBUIBILIDADE': d['ATRIBUIBILIDADE'],
                        'CAMADA': d['CAMADA'],
                        'TERMO_CULTURA': ctermo, 'TERMO_ALVO': atermo,
                        'TRECHO': trecho_que_casou(bruto, atermo),
                        'LINGUA_EVIDENCIA': lin_ev,
                    })

    # ── veredito por par ────────────────────────────────────────────────────────
    fora = []
    for (ck, ak), p in pares.items():
        n = sum(p['CAMADAS'].values())
        nf = len(p['FONTES'])
        if n < MIN_DOCS_PAR:
            estado, nivel = 'AMOSTRA_INSUFICIENTE', 'NAO_SEI'
        elif nf < MIN_FONTES_SOBE:
            estado, nivel = 'PASSA', 1
        elif len(p['PORTAS']) >= 2:
            estado, nivel = 'PASSA', 3
        else:
            estado, nivel = 'PASSA', 1
        cat = sorted(p['CATEGORIAS'])
        fora.append({
            'PAR': '%s x %s' % (ck, ak),
            'CULTURA': ck, 'ALVO': ak,
            'CATEGORIA_DE_PRODUTO': cat[0] if len(cat) == 1 else cat,
            'ESTADO': estado,
            'NIVEL': nivel,
            'NIVEL_2_ESTADO': 'NAO_MEDIDO — uma janela só, sem série comparável',
            'N_DOCUMENTOS': n,
            'N_FONTES_DISTINTAS': nf,
            'PORTAS_NATIVAS': sorted(p['PORTAS']),
            'CAMADAS': dict(p['CAMADAS']),
            'PLATEIA_DA_EVIDENCIA': dict(p['PLATEIAS']),
            'PLATEIA_VEREDITO': _veredito_plateia(p['PLATEIAS']),
            'PLATEIA_LEI': 'PROFESSIONAL_FIELD_AUDIENCE e HOBBY_GARDEN_AUDIENCE nao se somam. '
                           'Par sustentado so por canal de horta descreve conversa de jardim, '
                           'nao de lavoura.',
            'RECORTES_DE_ORIGEM': dict(p['RECORTES']),
            'RECORTE_LEI': 'o par aparece porque ABRIMOS este recorte. Nao aparecer em outro '
                           'recorte nao e ausencia no mundo.',
            'CERTEZA': {
                'CULTURA': 'OBSERVADO_NO_DOCUMENTO',
                'ALVO': 'OBSERVADO_NO_DOCUMENTO',
                'PAR': 'INFERIDO_PELO_SISTEMA',
                'CATEGORIA_DE_PRODUTO': 'INFERIDO_PELO_SISTEMA',
                'PORTA': 'DECLARADO_PELA_FONTE',
                'DATA_EVIDENCIA': 'DECLARADO_PELA_FONTE',
            },
            'POR_QUE_ENTROU': ('%d documentos, em %d portas nativas, de %d fontes '
                               'distintas, tratam de %s x %s.'
                               % (n, len(p['PORTAS']), nf, ck, ak)),
            'NAO_SEI': ['LOCAL_DO_FATO', 'TEMPO_DO_FATO', 'OCORRENCIA',
                        'SEVERIDADE', 'FALHA_DE_CONTROLE', 'RESISTENCIA',
                        'QUEM_FALA_NO_COMENTARIO'],
            'EVIDENCIAS': p['EVIDENCIAS'],
        })
    fora.sort(key=lambda r: (-(r['NIVEL'] if isinstance(r['NIVEL'], int) else 0),
                             -r['N_FONTES_DISTINTAS'], -r['N_DOCUMENTOS']))

    corpo = {
        'DATASET': 'IT-REGUA-FITOSSANITARIA-V0',
        'CONTRATO': 'docs/regras/REGUA-ITALIA-FITOSSANITARIA.md',
        'HERDADO_DE': 'portal-sintonia/REGUA-MISSAO-5-FITOSSANITARIO.md (Brasil, 23/08/2026)',
        'SOURCE_ID': 'DERIVED/IT-REGUA',
        'source': 'derivado do acervo SENSOR-PILOT — nenhuma coleta, nenhum custo',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'NAO_SEI — coocorrencia no texto nao e lugar do fato',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'CAPTURED_AT': '2026-09-02',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'UNIDADE': 'o PAR cultura x alvo. NUNCA o documento, NUNCA a fonte.',
        'DOCUMENTOS_LIDOS': total,
        'DESCARTES': {
            'TEXTO_CURTO': curtos,
            'SEM_PAR_NO_MESMO_TEXTO': barrados,
            'PAR_EM_LINGUA_NAO_ITALIANA': sem_lingua,
        },
        'LINGUA_DOS_DOCUMENTOS': dict(lingua_conta),
        'QUARENTENA_BARROU': dict(quarentena_barrou.most_common()),
        'PARES_TOTAL': len(fora),
        'PARES_POR_NIVEL': dict(Counter(str(r['NIVEL']) for r in fora)),
        'CORPUS_NAO_E_AMOSTRA_DA_CONVERSA': {
            'AVISO': 'a distribuicao por categoria abaixo segue OS RECORTES QUE ABRIMOS, '
                     'nao a conversa italiana. Em 01/09 herbicida era a maior categoria; '
                     'em 02/09 inseticida passou na frente — porque eu abri recortes de '
                     'melo, olivo e pomodoro, nao porque a Italia mudou de assunto.',
            'LEI': 'CORPUS E AMOSTRA DAS MINHAS CONSULTAS. Ler a distribuicao dele como '
                   'distribuicao do mundo e o erro mais facil desta camada.',
            'O_QUE_A_DISTRIBUICAO_MEDE': 'quanto de cada categoria EU procurei e achei',
            'O_QUE_ELA_NAO_MEDE': 'o que a Italia fala mais; nenhuma proporcao de mercado; '
                                  'nenhuma prevalencia de problema no campo',
        },
        'PARES_POR_CATEGORIA': dict(Counter(
            r['CATEGORIA_DE_PRODUTO'] if isinstance(r['CATEGORIA_DE_PRODUTO'], str)
            else '+'.join(r['CATEGORIA_DE_PRODUTO']) for r in fora)),
        'ASSUNTOS': {k: {'N': v['N'], 'PORTAS': sorted(v['PORTAS']),
                         'N_FONTES': len(v['FONTES'])} for k, v in assuntos.items()},
        'PORTAS_SEM_DADO': ['instagram+post', 'instagram+comentario',
                            'facebook+post_organico', 'x+post', 'tiktok+post',
                            'podcast+episodio', 'linkedin+post'],
        'PORTAS_SEM_DADO_LEI': ('PORTA AUSENTE NAO E RENDEU ZERO. Nenhuma linha deste '
                                'artefato pode ser lida como "nao se fala disso la".'),
        'AFIRMACOES_PROIBIDAS': [
            'o produtor relatou', 'ha falha de produto', 'ha resistencia',
            'ha oportunidade comercial', 'a praga esta ocorrendo em X',
            'o problema esta aumentando na Italia', 'X% dos produtores',
            'duas fontes confirmam', 'a praga e desta cultura',
        ],
        'PARES': fora,
    }
    os.makedirs(SAIDA, exist_ok=True)
    cam = os.path.join(SAIDA, 'IT-PARES-CULTURA-ALVO-V0.json')
    with open(cam, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('documentos lidos: %d' % total)
    print('  texto curto: %d · sem par: %d · par em lingua nao italiana: %d'
          % (curtos, barrados, sem_lingua))
    print('  lingua: %s' % dict(lingua_conta))
    print('  quarentena barrou: %s' % dict(quarentena_barrou.most_common(8)))
    print('PARES: %d · por nivel %s' % (len(fora), dict(Counter(str(r['NIVEL'])
                                                               for r in fora))))
    print('por categoria: %s' % corpo['PARES_POR_CATEGORIA'])
    print()
    print('%-34s %-6s %-5s %-5s %s' % ('PAR', 'NIVEL', 'DOCS', 'FONT', 'PORTAS'))
    for r in fora[:26]:
        print('%-34s %-6s %-5s %-5s %s'
              % (r['PAR'][:34], r['NIVEL'], r['N_DOCUMENTOS'],
                 r['N_FONTES_DISTINTAS'], len(r['PORTAS_NATIVAS'])))
    print('\ngravado: data/samples/IT-REGUA/IT-PARES-CULTURA-ALVO-V0.json')
    return 0


if __name__ == '__main__':
    sys.exit(medir())
