#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PESQUISADORES T6 — consultas por CULTURA + PROBLEMA, e a unidade «trabalho de pesquisador».

    py coleta/pesquisadores_t6.py --plano                 # as consultas e os pedidos por dominio
    py coleta/pesquisadores_t6.py --ensaio [--saida=F]    # SEM REDE: le as respostas gravadas
    py coleta/pesquisadores_t6.py --rede --rodada=N --saida=<pasta>   # COM REDE: so quem pode
    py coleta/pesquisadores_t6.py --ler --saida=<pasta>             # SEM REDE: le o que as rodadas guardaram

NAO E UM COLETOR NOVO
---------------------
O transporte e os lexicos sao os de `coleta/corpus_pesquisador.py` (a receita T6 do
orquestrador): o mesmo `_get` (nunca levanta: FALHA DE FONTE != ZERO), a mesma busca por
palavra inteira (`_tem`), o mesmo resumo a partir do indice invertido. O que este ficheiro
acrescenta e so o que la nao existe:

    1. as CONSULTAS por par cultura + problema (o corpus antigo so conhece 12 pessoas
       fechadas; aqui a pessoa nasce do trabalho, e nao o contrario);
    2. a UNIDADE com os campos do contrato T6 (DOI, TRIAL_ID/DATASET_ID, ORCID,
       instituicao, cultura, problema, molecula, local e periodo do estudo);
    3. a DEDUPLICACAO: mesma obra = uma unidade; mesmo ensaio = um grupo;
    4. o TETO de 5 pedidos por dominio por rodada, contado antes de pedir.

AS LEIS (herdadas, nenhuma afrouxada)
-------------------------------------
    AFILIACAO != LOCAL DO ENSAIO   a instituicao e do AUTOR; o local do estudo so vem do
                                   titulo/resumo, com o trecho que o sustentou
    PUBLICACAO != PERIODO          a data de publicacao nunca vira periodo do estudo
    ORCID NO INDICE != PROVA       o OpenAlex herda o ORCID do perfil e carimba-o em tudo;
                                   prova e o DOI na lista de obras do proprio ORCID
    CONSULTA != PROVA              a cultura e o problema da consulta nao passam para a
                                   unidade: so o que o texto do trabalho nomeia
    UNKNOWN NAO FUNDE              «provavel mesmo ensaio» agrupa para revisao; nao apaga
    SEM RANKING                    nenhuma nota, nenhuma ordem de importancia de pessoa
"""
import json
import os
import re
import sys
import time
import urllib.parse
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import corpus_pesquisador as CP  # noqa: E402  (transporte e lexicos da receita T6)

NAO_SEI = 'NAO SEI'
FIXTURES = os.path.join(RAIZ, 'tests', 'fixtures', 'pesquisadores_t6')
ATIVOS = os.path.join(RAIZ, 'referencia', 'adama', 'ACTIVE-INGREDIENTS.json')

OPENALEX = 'https://api.openalex.org/works'
CROSSREF = 'https://api.crossref.org/works'
ORCID_WORKS = 'https://pub.orcid.org/v3.0/%s/works'
DOMINIOS = ('api.openalex.org', 'api.crossref.org', 'pub.orcid.org')
TETO_POR_DOMINIO = 5          # D38: por dominio, por rodada
DOIS_POR_PEDIDO_CROSSREF = 40  # filtros doi: repetidos sao OU no Crossref
POR_PAGINA = 200
DESDE = '2019-01-01'
PAUSA = 3.0                   # a licao de 30/08 (universo_ciencia_it.py): devagar

# ── culturas do casco e problemas do Radar ─────────────────────────────────────
# Cada termo tem de APARECER no titulo/resumo. Italiano + ingles + nome cientifico.
CULTURAS = {
    'vite': ('grapevine', 'grapevines', 'vitis vinifera', 'vineyard', 'vineyards', 'viticulture',
             'vigneto', 'vigneti', 'viticoltura', 'grape', 'grapes'),
    'melo': ('apple', 'apples', 'malus domestica', 'apple orchard', 'melo', 'meleto', 'mela'),
    # sem «vite» e «mais» soltos: «vite» e tambem plural de «vita», «mais» e «mas» em
    # frances — o corpus_pesquisador ja mediu esse ruido e tirou-os pelo mesmo motivo
    'mais': ('maize', 'corn', 'zea mays', 'granoturco'),
    'pomodoro': ('tomato', 'tomatoes', 'solanum lycopersicum', 'pomodoro'),
}
PROBLEMAS = {
    'peronospora': ('plasmopara viticola', 'downy mildew', 'peronospora', 'phytophthora infestans',
                    'late blight'),
    'oidio': ('powdery mildew', 'erysiphe necator', 'podosphaera leucotricha', 'leveillula taurica',
              'oidium neolycopersici', 'oidio'),
    'botrite': ('botrytis cinerea', 'botrytis', 'grey mould', 'gray mold', 'bunch rot', 'botrite',
                'muffa grigia'),
    'tignoletta': ('lobesia botrana', 'european grapevine moth', 'grapevine moth', 'tignoletta'),
    'scafoideo': ('scaphoideus titanus', 'flavescence doree', 'flavescence', 'flavescenza dorata',
                  'scafoideo'),
    'piralide': ('ostrinia nubilalis', 'european corn borer', 'corn borer', 'piralide'),
    'diabrotica': ('diabrotica virgifera', 'western corn rootworm', 'rootworm', 'diabrotica'),
    'carpocapsa': ('cydia pomonella', 'codling moth', 'carpocapsa'),
}
# O par so existe onde o problema ataca a cultura. Doze pares, uma consulta cada.
PARES = [
    ('vite', 'peronospora'), ('vite', 'oidio'), ('vite', 'botrite'), ('vite', 'tignoletta'),
    ('vite', 'scafoideo'), ('melo', 'oidio'), ('melo', 'carpocapsa'), ('mais', 'piralide'),
    ('mais', 'diabrotica'), ('pomodoro', 'peronospora'), ('pomodoro', 'botrite'),
    ('pomodoro', 'oidio'),
]
# O termo da CONSULTA (curto, para o motor do OpenAlex). O da PROVA e o lexico acima.
CONSULTA_CULTURA = {
    'vite': '(grapevine OR vineyard OR "Vitis vinifera")',
    'melo': '(apple OR "Malus domestica")',
    'mais': '(maize OR corn OR "Zea mays")',
    'pomodoro': '(tomato OR "Solanum lycopersicum")',
}
CONSULTA_PROBLEMA = {
    ('vite', 'peronospora'): '("Plasmopara viticola" OR "downy mildew")',
    ('pomodoro', 'peronospora'): '("Phytophthora infestans" OR "late blight")',
    ('vite', 'oidio'): '("Erysiphe necator" OR "powdery mildew")',
    ('melo', 'oidio'): '("Podosphaera leucotricha" OR "powdery mildew")',
    ('pomodoro', 'oidio'): '("Leveillula taurica" OR "Oidium neolycopersici" OR "powdery mildew")',
    ('vite', 'botrite'): '("Botrytis cinerea" OR "bunch rot" OR "grey mould")',
    ('pomodoro', 'botrite'): '("Botrytis cinerea" OR "grey mould" OR "gray mold")',
    ('vite', 'tignoletta'): '("Lobesia botrana" OR "grapevine moth")',
    ('vite', 'scafoideo'): '("Scaphoideus titanus" OR "flavescence dorée")',
    ('mais', 'piralide'): '("Ostrinia nubilalis" OR "corn borer")',
    ('mais', 'diabrotica'): '("Diabrotica virgifera" OR rootworm)',
    ('melo', 'carpocapsa'): '("Cydia pomonella" OR "codling moth")',
}
CAMPOS_OPENALEX = ('id,doi,title,publication_date,type,authorships,abstract_inverted_index,'
                   'primary_location,primary_topic,ids')

# ── lugar do ESTUDO: so Italia, so pelo texto ────────────────────────────────
# As 20 regioes com o nome ingles ao lado (o resumo cientifico e em ingles). Provincia e
# comune NAO sao lidos aqui (o gazetteer do piloto, `leis/fato_local.py`, e italiano e e de
# outro dono): abaixo da regiao, o local do estudo fica NAO SEI.
# Isto e o lugar NOMEADO no resumo. Nomear nao prova que o ensaio foi la
# (PLACE_MENTION != FACT_LOCATION): o contrato chama-lhe LOCAL_DO_ESTUDO_ESCRITO.
REGIOES_EN = {
    'Piemonte': ('piedmont', 'piemonte'), 'Lombardia': ('lombardy', 'lombardia'),
    'Veneto': ('veneto',), 'Trentino-Alto Adige': ('trentino', 'south tyrol', 'alto adige',
                                                   'trentino-alto adige'),
    'Friuli-Venezia Giulia': ('friuli',), 'Liguria': ('liguria',),
    'Emilia-Romagna': ('emilia-romagna', 'emilia romagna'), 'Toscana': ('tuscany', 'toscana'),
    'Umbria': ('umbria',), 'Marche': ('marche',), 'Lazio': ('lazio', 'latium'),
    'Abruzzo': ('abruzzo',), 'Molise': ('molise',), 'Campania': ('campania',),
    'Puglia': ('apulia', 'puglia'), 'Basilicata': ('basilicata',), 'Calabria': ('calabria',),
    'Sicilia': ('sicily', 'sicilia'), 'Sardegna': ('sardinia', 'sardegna'),
    "Valle d'Aosta": ("aosta valley", "valle d'aosta"),
}
PAIS_IT = ('italy', 'italia')   # «italian» nao: «Italian cultivar» nao e lugar

# ── periodo do ESTUDO: anos escritos no resumo, presos a uma ancora de ensaio ──────
# ⚠️ lido a mao no ensaio: «In the 1990s» (a historia da doenca) dava periodo 1990. Ano
# seguido de «s» e decada, nao periodo do ensaio: (?![0-9s]) depois de cada ano.
_ANCORA_PERIODO = re.compile(
    r'(?:\b(?:in|during|over|from|between)\s+(?:the\s+)?(?:(?:growing\s+)?seasons?\s+|years?\s+)?'
    r'((?:19|20)\d\d)(?![0-9s])(?:\s*(?:-|–|to|and)\s*((?:19|20)\d\d)(?![0-9s]))?)'
    r'|(((?:19|20)\d\d)\s*(?:-|–)\s*((?:19|20)\d\d)\s+(?:growing\s+)?seasons?)', re.I)

# ── identificadores de ensaio/dataset que o texto pode trazer ────────────────────
_DATASET_DOI = re.compile(r'10\.(?:5281/zenodo\.\d+|5061/dryad\.[a-z0-9]+|6084/m9\.figshare\.\d+)',
                          re.I)
_TRIAL = re.compile(r'\b(?:EPPO\s+PP1/\d+|GEP\s+trial\s+[A-Z0-9-]+)\b', re.I)


def _ler(f):
    with open(f, encoding='utf-8') as h:
        return json.load(h)


def _moleculas():
    """Os 122 ativos do portfolio ADAMA Italia (T4). SO estes: o resto fica NAO SEI."""
    try:
        d = _ler(ATIVOS)
    except OSError:
        return {}
    out = {}
    for r in d.get('RECORDS', []):
        nome = (r.get('NAME') or '').strip()
        if len(nome) >= 4:                    # «2,4-D» e parecidos ficam de fora: casariam ruido
            out[nome.lower()] = r.get('ACTIVE_INGREDIENT_ID')
    return out


MOLECULAS = _moleculas()


# ═════════════════════════════════════════════ 1 · AS CONSULTAS E O TETO
def consultas():
    """→ lista de {PAR, BUSCA, URL}. Uma consulta por par, so a primeira pagina."""
    out = []
    for cult, prob in PARES:
        busca = '%s AND %s' % (CONSULTA_CULTURA[cult], CONSULTA_PROBLEMA[(cult, prob)])
        q = urllib.parse.urlencode({
            # institutions.country_code:it = ha um AUTOR com afiliacao italiana. E o filtro
            # de PESSOA (T6), nao de lugar do estudo.
            'filter': 'institutions.country_code:it,from_publication_date:%s,'
                      'title_and_abstract.search:%s' % (DESDE, busca),
            'per-page': POR_PAGINA, 'sort': 'publication_date:desc',
            'select': CAMPOS_OPENALEX, 'mailto': CP.MAILTO})
        out.append({'PAR': '%s x %s' % (cult, prob), 'CULTURA': cult, 'PROBLEMA': prob,
                    'BUSCA': busca, 'URL': OPENALEX + '?' + q})
    return out


def plano_de_rodadas(n_dois=0, n_pessoas=0):
    """Quantos pedidos por dominio, e em quantas rodadas cada dominio cabe no teto de 5.

    Os tres dominios andam em paralelo, cada um com o seu teto. So o OpenAlex e
    obrigatorio para a unidade existir; Crossref (prova da obra) e ORCID (prova da pessoa)
    sao INCREMENTAIS: sem eles a unidade existe com PROVA_DA_PESSOA = SO_INDICE, que nao e
    prova. A ordem das pessoas no ORCID e alfabetica — nao e ranking."""
    import math
    pedidos = {
        'api.openalex.org': len(PARES),
        'api.crossref.org': math.ceil(n_dois / DOIS_POR_PEDIDO_CROSSREF) if n_dois else 0,
        'pub.orcid.org': n_pessoas,
    }
    rodadas = {d: math.ceil(v / TETO_POR_DOMINIO) for d, v in pedidos.items()}
    return {'PEDIDOS_POR_DOMINIO': pedidos, 'TETO_POR_DOMINIO_POR_RODADA': TETO_POR_DOMINIO,
            'RODADAS_POR_DOMINIO': rodadas,
            'OBRIGATORIO': 'api.openalex.org (as 12 consultas: %d rodadas)' % rodadas['api.openalex.org'],
            'INCREMENTAL': ['api.crossref.org', 'pub.orcid.org']}


def url_crossref(dois):
    """Um pedido ao Crossref para varios DOI (filtros doi: repetidos sao OU)."""
    q = urllib.parse.urlencode({
        'filter': ','.join('doi:%s' % d for d in dois), 'rows': len(dois),
        'select': 'DOI,title,issued,type,author,container-title', 'mailto': CP.MAILTO})
    return CROSSREF + '?' + q


# ═════════════════════════════════════════════ 2 · LER AS RESPOSTAS
def resposta_valida(d):
    """O OpenAlex ja respondeu HTTP 200 com corpo de ERRO («Insufficient budget», 14/09).
    Isso nao e zero trabalhos: e FALHA_ORCAMENTO, com o corpo guardado."""
    if not isinstance(d, dict):
        return False, 'RESPOSTA_NAO_E_OBJETO'
    if 'error' in d or ('message' in d and 'results' not in d):
        return False, 'FALHA_ORCAMENTO_OU_ERRO: %s' % str(d.get('error') or d.get('message'))[:120]
    if 'results' not in d:
        return False, 'SEM_RESULTS'
    return True, ''


def _achados(lex, texto):
    """Todas as chaves do lexico que o texto sustenta, com o termo que sustentou."""
    out = []
    for chave, termos in lex.items():
        t = next((t for t in termos if CP._tem(t, texto)), None)
        if t:
            out.append({'VALOR': chave, 'TERMO': t})
    return out


def _local_do_estudo(texto_original):
    """Regiao italiana ou Italia NOMEADAS no titulo/resumo, com o trecho. Nunca afiliacao."""
    t = CP._texto(texto_original)
    regs = [{'VALOR': reg, 'PRECISAO': 'REGIAO', 'TERMO': termo, 'ORIGEM': 'ESCRITO'}
            for reg, termos in REGIOES_EN.items()
            for termo in [next((x for x in termos if CP._tem(x, t)), None)] if termo]
    if regs:
        return regs
    pais = next((x for x in PAIS_IT if CP._tem(x, t)), None)
    if pais:
        return [{'VALOR': 'Italia', 'PRECISAO': 'PAIS', 'TERMO': pais, 'ORIGEM': 'ESCRITO'}]
    return []


def _periodo_do_estudo(resumo):
    """Anos do ENSAIO escritos no resumo, presos a «in/during/over/from/between» ou a
    «seasons». A data de publicacao nunca entra aqui."""
    out = []
    for m in _ANCORA_PERIODO.finditer(resumo or ''):
        a, b = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(5))
        out.append({'DE': a, 'ATE': b or a, 'TRECHO': m.group(0).strip()[:80]})
    return out


def _doi(x):
    return (x or '').replace('https://doi.org/', '').strip().lower() or None


def unidade(w, pares_da_consulta):
    """Um trabalho do OpenAlex → a unidade do contrato T6. Cada campo com a prova ou NAO SEI."""
    titulo = w.get('title') or w.get('display_name') or ''
    resumo = CP._resumo_do_indice(w.get('abstract_inverted_index'))
    texto = CP._texto(titulo + ' . ' + resumo)
    doi = _doi(w.get('doi'))

    autores = []
    for a in w.get('authorships') or []:
        au = a.get('author') or {}
        insts = [{'NOME': i.get('display_name'), 'PAIS': i.get('country_code') or NAO_SEI,
                  'ROR': i.get('ror') or NAO_SEI} for i in (a.get('institutions') or [])]
        autores.append({
            'OPENALEX_ID': au.get('id'), 'NOME': au.get('display_name'),
            # ⚠️ o ORCID do indice e herdado do perfil: fica marcado, nao e prova
            'ORCID_NO_INDICE': (au.get('orcid') or '').replace('https://orcid.org/', '') or NAO_SEI,
            'PROVA_DA_PESSOA': 'SO_INDICE',
            'INSTITUICOES_NESTA_OBRA': insts or NAO_SEI,
            'AFILIACAO_ITALIANA_NESTA_OBRA': any(i['PAIS'] == 'IT' for i in insts),
        })

    dataset = []
    if (w.get('type') or '') == 'dataset' and doi:
        dataset.append({'ID': doi, 'COMO': 'o proprio trabalho e um dataset'})
    for m in _DATASET_DOI.finditer(resumo):
        dataset.append({'ID': m.group(0).lower(), 'COMO': 'DOI de dataset escrito no resumo'})
    trial = [{'ID': m.group(0), 'COMO': 'escrito no resumo'} for m in _TRIAL.finditer(resumo)]

    moleculas = [{'VALOR': nome, 'ACTIVE_INGREDIENT_ID': aid}
                 for nome, aid in MOLECULAS.items() if CP._tem(nome, texto)]

    return {
        'UNIDADE': 'TRABALHO_DE_PESQUISADOR',
        'DOI': doi or NAO_SEI,
        'OPENALEX_WORK_ID': w.get('id'),
        'TITULO': titulo,
        'TIPO': CP._tipo_material(w),
        'PUBLICADO_EM': w.get('publication_date') or NAO_SEI,
        'TRIAL_ID': trial or NAO_SEI,
        'DATASET_ID': dataset or NAO_SEI,
        'AUTORES': autores,
        'CULTURA': _achados(CULTURAS, texto) or NAO_SEI,
        'PROBLEMA': _achados(PROBLEMAS, texto) or NAO_SEI,
        'MOLECULA': moleculas or NAO_SEI,
        'MOLECULA_LEXICO': 'so os %d ativos do portfolio ADAMA Italia (referencia/adama)' % len(MOLECULAS),
        'LOCAL_DO_ESTUDO_ESCRITO': _local_do_estudo(titulo + ' . ' + resumo) or NAO_SEI,
        'PERIODO_DO_ESTUDO': _periodo_do_estudo(resumo) or NAO_SEI,
        'CONSULTAS_QUE_O_TROUXERAM': sorted(pares_da_consulta),
        'NA_CONSULTA_E_NO_TEXTO': sorted(
            p for p in pares_da_consulta
            if any(c['VALOR'] == p.split(' x ')[0] for c in (_achados(CULTURAS, texto)))
            and any(c['VALOR'] == p.split(' x ')[1] for c in (_achados(PROBLEMAS, texto)))),
    }


def dois_do_orcid(d):
    """Os DOI que a PROPRIA pessoa declarou no ORCID (/works, relacao self)."""
    out = set()
    for g in (d or {}).get('group') or []:
        for e in ((g.get('external-ids') or {}).get('external-id') or []):
            if (e.get('external-id-type') == 'doi'
                    and (e.get('external-id-relationship') or 'self') == 'self'):
                out.add(_doi(e.get('external-id-value')))
    out.discard(None)
    return out


def provar_pessoas(unidades, orcid_por_id):
    """PROVA_DA_PESSOA = ORCID_AUTODECLARADO quando o DOI esta no /works do proprio ORCID."""
    for u in unidades:
        for a in u['AUTORES']:
            oid = a['ORCID_NO_INDICE']
            if oid in orcid_por_id:
                a['PROVA_DA_PESSOA'] = ('ORCID_AUTODECLARADO' if u['DOI'] in orcid_por_id[oid]
                                        else 'ORCID_LIDO_SEM_ESTE_DOI')
    return unidades


def provar_por_crossref(unidades, resposta):
    """O Crossref guarda, obra a obra, o ORCID que o EDITOR depositou para cada autor (e
    `authenticated-orcid` quando a propria pessoa o confirmou no deposito). Isso e prova da
    OBRA, nao heranca do perfil — mais fraca que o /works do proprio ORCID, mais forte que o
    indice. 1 pedido cobre DOIS_POR_PEDIDO_CROSSREF obras; o ORCID pede 1 por pessoa.

    ⚠️ NENHUMA resposta real do Crossref foi gravada nesta casa: os nomes dos campos sao os
    da documentacao publica da API e a primeira rodada com rede e que os prova."""
    ok = isinstance(resposta, dict) and isinstance((resposta.get('message') or {}).get('items'), list)
    if not ok:
        return {'OK': False, 'PORQUE': 'resposta do Crossref sem message.items'}
    por_doi = {}
    for it in resposta['message']['items']:
        por_doi[_doi(it.get('DOI'))] = it
    confirmados = 0
    for u in unidades:
        it = por_doi.get(u['DOI'])
        if it is None:
            continue
        confirmados += 1
        u['CROSSREF_CONFIRMA_DOI'] = True
        dep = {}
        for au in it.get('author') or []:
            oid = (au.get('ORCID') or '').rstrip('/').rsplit('/', 1)[-1]
            if oid:
                dep[oid] = bool(au.get('authenticated-orcid'))
        for a in u['AUTORES']:
            if a['PROVA_DA_PESSOA'] == 'ORCID_AUTODECLARADO':
                continue                         # a prova mais forte nao e rebaixada
            if a['ORCID_NO_INDICE'] in dep:
                a['PROVA_DA_PESSOA'] = ('ORCID_NO_DEPOSITO_AUTENTICADO' if dep[a['ORCID_NO_INDICE']]
                                        else 'ORCID_NO_DEPOSITO_DO_EDITOR')
    return {'OK': True, 'DOIS_CONFIRMADOS': confirmados}


# ═════════════════════════════════════════════ 3 · DEDUPLICAR
def _titulo_norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', CP._texto(t)).strip()


def deduplicar(brutos):
    """brutos: [(trabalho_openalex, par)] → unidades.

    MESMA OBRA (mesmo DOI, ou mesmo id OpenAlex sem DOI) → UMA unidade, com todas as
    consultas que a trouxeram. MESMO ENSAIO provado (mesmo TRIAL_ID/DATASET_ID) → um grupo
    ENSAIO_PROVADO. Mesmo titulo + um autor em comum, DOI diferente (preprint e artigo) →
    grupo PROVAVEL_MESMA_OBRA, para revisao: nada e apagado nem fundido.
    """
    por_chave, pares = {}, defaultdict(set)
    for w, par in brutos:
        k = _doi(w.get('doi')) or w.get('id')
        por_chave.setdefault(k, w)
        pares[k].add(par)
    unidades = [unidade(w, pares[k]) for k, w in por_chave.items()]

    grupos = []
    por_id = defaultdict(list)
    for u in unidades:
        for campo in ('TRIAL_ID', 'DATASET_ID'):
            if u[campo] != NAO_SEI:
                for x in u[campo]:
                    por_id[x['ID'].lower()].append(u['DOI'])
    for i, dois in por_id.items():
        if len(set(dois)) > 1:
            grupos.append({'ESTADO': 'ENSAIO_PROVADO', 'POR': i, 'DOIS': sorted(set(dois))})

    por_titulo = defaultdict(list)
    for u in unidades:
        por_titulo[_titulo_norm(u['TITULO'])].append(u)
    for t, us in por_titulo.items():
        if len(us) < 2 or not t:
            continue
        ids = [set(a['OPENALEX_ID'] for a in u['AUTORES']) for u in us]
        if set.intersection(*ids):
            grupos.append({'ESTADO': 'PROVAVEL_MESMA_OBRA', 'POR': 'mesmo titulo + autor em comum',
                           'DOIS': sorted(u['DOI'] for u in us)})
    return unidades, grupos


# ═════════════════════════════════════════════ 4 · PESSOAS (T6) A PARTIR DAS UNIDADES
def pessoas(unidades):
    """Quem tem afiliacao italiana NUM trabalho — por problema, nunca ordenado por nota."""
    p = {}
    for u in unidades:
        for a in u['AUTORES']:
            if not a['AFILIACAO_ITALIANA_NESTA_OBRA']:
                continue
            r = p.setdefault(a['OPENALEX_ID'], {
                'OPENALEX_ID': a['OPENALEX_ID'], 'NOME': a['NOME'], 'ORCID': a['ORCID_NO_INDICE'],
                'INSTITUICOES_ITALIANAS': set(), 'DOIS': set(), 'PARES_NO_TEXTO': set(),
                'PROVAS': set()})
            r['INSTITUICOES_ITALIANAS'].update(i['NOME'] for i in a['INSTITUICOES_NESTA_OBRA']
                                               if i['PAIS'] == 'IT' and i['NOME'])
            r['DOIS'].add(u['DOI'])
            r['PARES_NO_TEXTO'].update(u['NA_CONSULTA_E_NO_TEXTO'])
            r['PROVAS'].add(a['PROVA_DA_PESSOA'])
    out = []
    for r in p.values():
        out.append({k: (sorted(v) if isinstance(v, set) else v) for k, v in r.items()})
    out.sort(key=lambda r: (r['NOME'] or ''))       # ordem ALFABETICA: nao e ranking
    return out


ATLAS = os.path.join(RAIZ, 'docs', 'fontes', 'ATLAS-DE-FONTES-EAME.md')


def orcids_do_atlas():
    """ORCID → SOURCE_ID das fontes que o Atlas ja tem (IT-T6-001..036 hoje)."""
    try:
        a = open(ATLAS, encoding='utf-8').read()
    except OSError:
        return {}
    out = {}
    for sid, url in re.findall(r'SOURCE_ID:\s+(IT-T\d+-\d+)\s.*?URL:\s+(\S+)', a, re.S):
        m = re.search(r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', url)
        if m:
            out[m.group(1)] = sid
    return out


def fichas_candidatas(gente, unidades, atlas=None):
    """O degrau 1 do caminho canonico: cada pessoa → os argumentos de
    `candidatas/fonte_nova.registar(...)`. NAO grava: quem regista e quem corre a porta.

    So entra quem tem ORCID (o endereco canonico da fonte T6) e pelo menos um par
    cultura+problema NOMEADO no texto de um trabalho seu. PAIS=IT e o pais da PESSOA pela
    afiliacao escrita na autoria — nunca o do estudo — e a prova vai na NOTA."""
    doi_titulo = {u['DOI']: u['TITULO'] for u in unidades}
    atlas = orcids_do_atlas() if atlas is None else atlas
    out, sem_orcid = [], 0
    for p in gente:
        if not p['PARES_NO_TEXTO']:
            continue
        if p['ORCID'] == NAO_SEI:
            sem_orcid += 1
            continue
        if p['ORCID'] in atlas:
            # ja e fonte: nao nasce outra. Fica listada para o contrato, com o numero que tem.
            out.append({'JA_E_FONTE': atlas[p['ORCID']], 'url': 'https://orcid.org/%s' % p['ORCID'],
                        'para_que': 'T6 pesquisador: %s' % '; '.join(p['PARES_NO_TEXTO'])})
            continue
        out.append({
            'tipo': 'CIENCIA', 'pais': 'IT',
            'nome': '%s — registo ORCID (pesquisador)' % p['NOME'],
            'url': 'https://orcid.org/%s' % p['ORCID'],
            'para_que': 'T6 pesquisador: %s' % '; '.join(p['PARES_NO_TEXTO']),
            'quem_viu': 'PESQUISADORES-T6 (coleta/pesquisadores_t6.py)',
            'onde_viu': 'OpenAlex: ' + ', '.join(p['DOIS'][:3]),
            'nota': ('PAIS_PROVA=afiliacao italiana na autoria (%s) de %s «%s»; pais da PESSOA, '
                     'nao do estudo. PROVA_DA_PESSOA=%s. ORCID do indice OpenAlex.'
                     % ('; '.join(p['INSTITUICOES_ITALIANAS'][:2]), p['DOIS'][0],
                        (doi_titulo.get(p['DOIS'][0]) or '')[:80], ','.join(p['PROVAS']))),
        })
    return out, sem_orcid


# ═════════════════════════════════════════════ 5 · ENSAIO OFFLINE
def ensaio(pasta=FIXTURES):
    """Corre a leitura inteira sobre as respostas GRAVADAS. Zero pedidos a rede."""
    man = _ler(os.path.join(pasta, 'MANIFEST.json'))
    brutos, invalidas = [], []
    for f in man['OPENALEX']:
        d = _ler(os.path.join(pasta, f['FICHEIRO']))
        ok, porque = resposta_valida(d)
        if not ok:
            invalidas.append({'FICHEIRO': f['FICHEIRO'], 'PORQUE': porque})
            continue
        for w in d['results']:
            texto = CP._texto((w.get('title') or '') + ' . '
                              + CP._resumo_do_indice(w.get('abstract_inverted_index')))
            # o que a consulta do par TERIA trazido: o par tem de estar no texto (o motor do
            # OpenAlex busca titulo+resumo) e um autor com afiliacao italiana
            it = any((i.get('country_code') == 'IT') for a in (w.get('authorships') or [])
                     for i in (a.get('institutions') or []))
            if not it:
                continue
            for cult, prob in PARES:
                if (any(CP._tem(t, texto) for t in CULTURAS[cult])
                        and any(CP._tem(t, texto) for t in PROBLEMAS[prob])):
                    brutos.append((w, '%s x %s' % (cult, prob)))
    orcid = {}
    for f in man['ORCID']:
        orcid[f['ORCID']] = dois_do_orcid(_ler(os.path.join(pasta, f['FICHEIRO'])))
    unidades, grupos = deduplicar(brutos)
    provar_pessoas(unidades, orcid)
    gente = pessoas(unidades)
    conta = lambda campo: sum(1 for u in unidades if u[campo] != NAO_SEI)  # noqa: E731
    por_par = defaultdict(int)
    for u in unidades:
        for p in u['NA_CONSULTA_E_NO_TEXTO']:
            por_par[p] += 1
    return {
        'ENSAIO': 'OFFLINE — respostas gravadas, zero pedidos',
        'FIXTURES': man.get('ORIGEM'),
        'RESPOSTAS_INVALIDAS': invalidas,
        'OCORRENCIAS_PAR_TRABALHO': len(brutos),
        'UNIDADES_DEPOIS_DE_DEDUPLICAR': len(unidades),
        'GRUPOS': grupos,
        'POR_PAR': dict(sorted(por_par.items())),
        'CAMPOS_PREENCHIDOS': {c: conta(c) for c in ('DOI', 'TRIAL_ID', 'DATASET_ID', 'CULTURA',
                                                     'PROBLEMA', 'MOLECULA', 'LOCAL_DO_ESTUDO_ESCRITO',
                                                     'PERIODO_DO_ESTUDO')},
        'PESSOAS_COM_AFILIACAO_IT': len(gente),
        'PESSOAS_COM_ORCID_AUTODECLARADO': sum(1 for g in gente if 'ORCID_AUTODECLARADO' in g['PROVAS']),
        'CANDIDATAS_T6_PROPOSTAS': len(fichas_candidatas(gente, unidades)[0]),
        'PESSOAS_COM_PAR_NO_TEXTO_SEM_ORCID': fichas_candidatas(gente, unidades)[1],
        'PLANO_SE_FOSSE_REDE': plano_de_rodadas(
            n_dois=sum(1 for u in unidades if u['DOI'] != NAO_SEI),
            n_pessoas=sum(1 for g in gente if g['ORCID'] != NAO_SEI)),
        'UNIDADES': unidades,
        'PESSOAS': gente,
    }


# ═════════════════════════════════════════════ 6 · REDE (so quem pode a corre)
def _guardar(saida, nome, d):
    """Guarda a resposta TAL COMO VEIO (ou vazio, se nao veio nada) e devolve o sha256."""
    import hashlib
    corpo = json.dumps(d, ensure_ascii=False) if d is not None else ''
    with open(os.path.join(saida, nome), 'w', encoding='utf-8', newline='\n') as h:
        h.write(corpo)
    return hashlib.sha256(corpo.encode('utf-8')).hexdigest()


def _estado(saida):
    f = os.path.join(saida, 'ESTADO.json')
    return _ler(f) if os.path.exists(f) else {'OPENALEX_PARES_FEITOS': [], 'CROSSREF_DOIS_FEITOS': [],
                                              'ORCID_FEITOS': [], 'RODADAS': []}


def _pedir(url, chave=None):
    if chave:                                  # so se o dono tiver chave do OpenAlex
        url += '&api_key=' + urllib.parse.quote(chave)
    return CP._get(url)


def rodada_com_rede(n, saida, pausa=PAUSA, chave_openalex=None):
    """UMA rodada, <= TETO_POR_DOMINIO pedidos em CADA um dos 3 dominios, contados antes:

        A. OpenAlex  — os proximos pares ainda sem resposta valida (12 pares = 3 rodadas)
        B. Crossref  — os DOI ja trazidos e ainda nao conferidos, 40 por pedido
        C. ORCID     — /works das pessoas com ORCID ainda nao lidas, por ordem ALFABETICA

    Cada resposta fica guardada tal como veio, com o sha256 no RODADA-n.json. O primeiro
    corpo de ERRO num dominio (ex.: «Insufficient budget» com HTTP 200) PARA esse dominio
    na rodada: nao e zero, nao se insiste, e o par fica por fazer."""
    os.makedirs(saida, exist_ok=True)
    est = _estado(saida)
    registo = {'RODADA': n, 'PEDIDOS': {d: 0 for d in DOMINIOS}, 'RESPOSTAS': []}

    def anotar(dom, nome, d, ok, porque, extra=None):
        registo['PEDIDOS'][dom] += 1
        assert registo['PEDIDOS'][dom] <= TETO_POR_DOMINIO, 'teto por dominio passado'
        nome = nome if ok else 'FALHA-r%d-%s' % (n, nome)
        registo['RESPOSTAS'].append(dict({'DOMINIO': dom, 'FICHEIRO': nome, 'SHA256': _guardar(saida, nome, d),
                                          'OK': ok, 'PORQUE': porque}, **(extra or {})))

    # A · OpenAlex
    for q in [q for q in consultas() if q['PAR'] not in est['OPENALEX_PARES_FEITOS']][:TETO_POR_DOMINIO]:
        d, err = _pedir(q['URL'], chave_openalex)
        ok, porque = resposta_valida(d) if d is not None else (False, err)
        anotar('api.openalex.org', 'openalex-%s.json' % q['PAR'].replace(' x ', '-'), d, ok, porque,
               {'PAR': q['PAR'], 'CONTAGEM_DECLARADA': d.get('meta', {}).get('count') if ok else None,
                'NA_PAGINA': len(d.get('results') or []) if ok else None})
        if not ok:
            break
        est['OPENALEX_PARES_FEITOS'].append(q['PAR'])
        time.sleep(pausa)

    unidades, _, gente = ler_pasta(saida, com_provas=False)

    # B · Crossref
    faltam = sorted(u['DOI'] for u in unidades
                    if u['DOI'] != NAO_SEI and u['DOI'] not in est['CROSSREF_DOIS_FEITOS'])
    for i in range(0, min(len(faltam), TETO_POR_DOMINIO * DOIS_POR_PEDIDO_CROSSREF), DOIS_POR_PEDIDO_CROSSREF):
        lote = faltam[i:i + DOIS_POR_PEDIDO_CROSSREF]
        d, err = CP._get(url_crossref(lote))
        ok = isinstance(d, dict) and isinstance((d.get('message') or {}).get('items'), list)
        anotar('api.crossref.org', 'crossref-r%d-%d.json' % (n, i // DOIS_POR_PEDIDO_CROSSREF + 1), d, ok,
               '' if ok else (err or 'sem message.items'), {'DOIS_PEDIDOS': len(lote)})
        if not ok:
            break
        est['CROSSREF_DOIS_FEITOS'].extend(lote)
        time.sleep(pausa)

    # C · ORCID (alfabetico: nao e ranking)
    for p in [g for g in gente if g['ORCID'] != NAO_SEI and g['ORCID'] not in est['ORCID_FEITOS']][:TETO_POR_DOMINIO]:
        d, err = CP._get(ORCID_WORKS % p['ORCID'])
        ok = isinstance(d, dict) and 'group' in d
        anotar('pub.orcid.org', 'orcid-%s-works.json' % p['ORCID'], d, ok, '' if ok else (err or 'sem group'),
               {'ORCID': p['ORCID']})
        if not ok:
            break
        est['ORCID_FEITOS'].append(p['ORCID'])
        time.sleep(pausa)

    est['RODADAS'].append({'RODADA': n, 'PEDIDOS': registo['PEDIDOS']})
    with open(os.path.join(saida, 'ESTADO.json'), 'w', encoding='utf-8', newline='\n') as h:
        json.dump(est, h, ensure_ascii=False, indent=1)
    with open(os.path.join(saida, 'RODADA-%d.json' % n), 'w', encoding='utf-8', newline='\n') as h:
        json.dump(registo, h, ensure_ascii=False, indent=1)
    return registo


def ler_pasta(saida, com_provas=True):
    """As respostas guardadas pelas rodadas → (unidades, grupos, pessoas). Sem rede."""
    brutos = []
    for f in sorted(os.listdir(saida)):
        if f.startswith('openalex-') and f.endswith('.json'):
            d = _ler(os.path.join(saida, f))
            if resposta_valida(d)[0]:
                par = f[len('openalex-'):-len('.json')].replace('-', ' x ', 1)
                brutos.extend((w, par) for w in d['results'])
    unidades, grupos = deduplicar(brutos)
    if com_provas:
        orcid = {f[len('orcid-'):-len('-works.json')]: dois_do_orcid(_ler(os.path.join(saida, f)))
                 for f in os.listdir(saida) if f.startswith('orcid-') and f.endswith('-works.json')}
        provar_pessoas(unidades, orcid)
        for f in sorted(os.listdir(saida)):
            if f.startswith('crossref-') and f.endswith('.json'):
                provar_por_crossref(unidades, _ler(os.path.join(saida, f)))
    return unidades, grupos, pessoas(unidades)


def main(argv):
    opt = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '1') for a in argv if a.startswith('--'))
    if 'plano' in opt:
        print(json.dumps({'CONSULTAS': [{k: q[k] for k in ('PAR', 'BUSCA')} for q in consultas()],
                          'PLANO': plano_de_rodadas()}, ensure_ascii=False, indent=1))
        return 0
    if 'ensaio' in opt:
        r = ensaio(opt.get('fixtures', FIXTURES))
        if opt.get('saida'):
            with open(opt['saida'], 'w', encoding='utf-8', newline='\n') as h:
                json.dump(r, h, ensure_ascii=False, indent=1)
        print(json.dumps({k: v for k, v in r.items() if k not in ('UNIDADES', 'PESSOAS')},
                         ensure_ascii=False, indent=1))
        return 0
    if 'rede' in opt or 'ler' in opt:
        if not opt.get('saida'):
            print('falta --saida=<pasta>')
            return 2
        if 'rede' in opt:
            r = rodada_com_rede(int(opt.get('rodada', '1')), opt['saida'],
                                chave_openalex=os.environ.get('OPENALEX_API_KEY') or None)
            print(json.dumps(r, ensure_ascii=False, indent=1))
        us, gs, gente = ler_pasta(opt['saida'])
        with open(os.path.join(opt['saida'], 'UNIDADES-T6.json'), 'w', encoding='utf-8', newline='\n') as h:
            json.dump({'UNIDADES': us, 'GRUPOS': gs, 'PESSOAS': gente,
                       'CANDIDATAS_T6_PROPOSTAS': fichas_candidatas(gente, us)[0]}, h, ensure_ascii=False, indent=1)
        print(json.dumps({'UNIDADES': len(us), 'GRUPOS': len(gs), 'PESSOAS_COM_AFILIACAO_IT': len(gente)}))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
