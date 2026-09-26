#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONCORRENZA — EMPRESA + PRODUTO + CULTURA/PROBLEMA + LUGAR + TEMPO + TIPO.

    py coleta/comunicacao_concorrenza.py            # mede sobre as 561 atividades do repo

A ferramenta CONCORRENZA do casco cruza `empresa + produto + cultura + lugar +
tempo`, validado no registo T4 (decisao D84). O classificador vizinho
(`comunicacao_classificar.py`) ja le tipo, cultura, problema e pais — e deixa
EMPRESA e PRODUTO em `NOT_KNOWN` de proposito. Este ficheiro preenche os dois, e
SO os dois, reusando as tabelas de la: uma logica, um dono (INT-LAW-282).

A LEI QUE MANDA AQUI: O QUE A EMPRESA DIZ NAO E O QUE O REGISTO PROVA
-----------------------------------------------------------------------
Biblia da Intelligence, CAP-COMP:

    COMPANY_CLAIM != REGULATORY_FACT — e as duas camadas NUNCA partilham contagem
    comunicacao e alegacao ate prova em contrario

Por isso cada saida tem DUAS listas que nunca se somam:

    ALEGACOES            o que o texto da empresa afirma (desempenho, e tambem
                         o que ela diz sobre registo — «autorizzato su vite» e
                         uma ALEGACAO regulatoria, nao um facto)
    FACTOS_REGULATORIOS  so o que veio do REGISTO T4: um item que E registo, ou
                         a resposta do registo a um produto nomeado

E o registo tambem nao diz tudo (INT-LAW-067):

    REGISTRATION != SALES   ·   REGISTRATION != COMMERCIAL_AVAILABILITY

O QUE E PROVA DE PRODUTO
-------------------------
So o nome marcado com ® ou ™ no proprio texto — a mesma prova que o pacote ja
usa (`MARCA_REGISTRADA_NO_TEXTO`, pacote/pacote_camadas.py). Nome em maiusculas
sem a marca NAO e extraido: «RESA» num anuncio e a palavra resa, nao um produto.

⚠️ NEM TODA MARCA REGISTADA E UM PRODUTO. Medido nas 561 atividades: «Belanty®,
a base di Revysol®» — Revysol e a marca da SUBSTANCIA ATIVA, nao um formulado
que se compra. O pacote contava os dois como produto. Aqui, uma marca que vem
logo depois de «a base di», «based on», «contenente», «combinazione di» vai
para MARCAS_DE_SUBSTANCIA e nao para PRODUTOS.

O QUE ESTE FICHEIRO NUNCA FAZ
------------------------------
* nao adivinha a empresa pela lingua, pela imagem ou por uma palavra solta: a
  empresa que FALA vem do canal/conta declarado pela coleta; empresas
  nomeadas no texto ficam numa lista a parte (EMPRESAS_NOMEADAS);
* nao da tempo de facto: a data do anuncio e a data da COMUNICACAO
  (INT-LAW-101 / RT-TOOL-06). `FACT_TIME` nasce e fica `NAO SEI`;
* nao cria ID de produto: `PRODUCT_ID` so existe se o registo T4 devolver um
  numero de registo;
* nao le o registo T4 por conta propria: recebe um objeto que o saiba ler
  (`CONTRATO_DO_REGISTO_T4`). O parser do registo e de outra sessao — aqui
  vive so a tomada.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import comunicacao_classificar as cl  # noqa: E402
from adama_referencia import chave as chave_do_nome  # noqa: E402

NAO_SEI = "NAO SEI"
EXTRATOR = "CONCORRENZA-V1"

# ── EMPRESAS ─────────────────────────────────────────────────────────────────
# A MESMA lista de pacote/pacote_camadas.py:MARCAS (o teste prova que nao
# divergem). Nao se importa de la porque aquele modulo arrasta o normalizador do
# pacote e o git; a igualdade e vigiada em vez de copiada as cegas.
MARCAS = ['bayer', 'syngenta', 'corteva', 'basf', 'fmc', 'upl', 'sipcam',
          'certis', 'gowan', 'nufarm', 'belchim', 'sumitomo']
# A ADAMA e o cliente: aparece, mas nunca como concorrente.
PROPRIA = 'adama'


def _empresas_em(texto_norm: str) -> list[str]:
    fora = []
    for m in MARCAS + [PROPRIA]:
        if re.search(r'(?<![a-z0-9])%s(?![a-z0-9])' % re.escape(m), texto_norm):
            fora.append(m.upper())
    return fora


def empresa_que_fala(item: dict) -> tuple[str, str]:
    """(EMPRESA, BASE). So o canal/conta declarado pela coleta decide quem fala.

    Um texto de revista que cita a BASF nao e comunicacao da BASF. Por isso o
    corpo do texto nunca e lido aqui.
    """
    for campo, base in (('COMPANY', 'DECLARADA_PELA_COLETA'),
                        ('ACCOUNT', 'CONTA_PROPRIA'), ('PAGE', 'PAGINA_PROPRIA'),
                        ('CHANNEL', 'CANAL_PROPRIO')):
        v = item.get(campo)
        if not v or v == cl.NAO_SEI:
            continue
        achadas = _empresas_em(cl._norm(v))
        if len(achadas) == 1:
            return achadas[0], '%s: %s=«%s»' % (base, campo, v)
        if len(achadas) > 1:
            return NAO_SEI, '%s nomeia mais de uma empresa (%s) — nao se escolhe' % (
                campo, ', '.join(achadas))
    return NAO_SEI, 'a coleta nao declarou canal/conta de empresa conhecida'


# ── PRODUTOS ─────────────────────────────────────────────────────────────────
# O token com maiuscula logo antes de ® ou ™. Um token so: «Syngenta Vegetables
# Seeds Angello®» e Angello, nao «Seeds Angello».
_RE_MARCA = re.compile(r"([A-ZÀ-Ý0-9][\w\-]*[\w])\s?(?:®|™|\(R\)|\(TM\))")
# O que, dito logo antes da marca, faz dela SUBSTANCIA e nao produto.
_RE_ANTES_DE_SUBSTANCIA = re.compile(
    r"(?:a\s+base\s+di|based\s+on|contenente|contiene|combinazione\s+di|"
    r"sostanza\s+attiva|principio\s+attivo|molecola|con\s+la\s+tecnologia|"
    r"tecnologia|a\s+base\s+de|basado\s+en|a\s+base\s+du?|"
    # medidos nas 561: «il fungicida con Revysol®», «nasce dall'unione di
    # Revysol® e protioconazolo», «Formulating SOLATENOL™»
    r"(?:fungicida|insetticida|erbicida|acaricida|nematocida)\s+con|"
    r"unione\s+di|formulating)\s*$", re.I)


# O que, dito logo DEPOIS da marca, tambem a faz substancia/tecnologia:
# «Inatreq™ active», «Axalion® Active», «Zorvec™ technology» (medido nas 561).
_RE_DEPOIS_DE_SUBSTANCIA = re.compile(
    r"^\s*(?:active|attiv[oa]|technology|tecnologia|technologie|tecnolog[ií]a)(?![a-z])", re.I)


def marcas_do_texto(texto: str) -> dict:
    """{'PRODUTOS': [...], 'MARCAS_DE_SUBSTANCIA': [...]} — ordem de aparicao, sem repetir."""
    prods, subs, vistos = [], [], {}
    for m in _RE_MARCA.finditer(texto or ''):
        nome = m.group(1)
        if nome.lower() in MARCAS or nome.lower() == PROPRIA:
            continue          # o nome da empresa com ® nao e um produto
        antes = (texto[max(0, m.start() - 40):m.start()])
        # «Corteva Agriscience™»: a marca que vem colada ao nome da empresa e a
        # propria empresa, nao um produto
        ultima = re.findall(r"[\w\-]+", antes[-20:])
        if ultima and ultima[-1].lower() in MARCAS + [PROPRIA]:
            continue
        # «OMNERA®» e «Omnera®» sao o mesmo nome: fica a primeira grafia
        nome = vistos.setdefault(chave_do_nome(nome), nome)
        if _RE_DEPOIS_DE_SUBSTANCIA.search(texto[m.end():m.end() + 20]):
            if nome not in subs:
                subs.append(nome)
            continue
        # a marca anterior tambem conta como ponte: «a base di F500® e Xemium®».
        # So a CONJUNCAO liga; a virgula nao — «principio attivo Cyazypyr®,
        # Exirel® ...» e aposto: Exirel e o produto (medido nas 561).
        antes_sem_marcas = re.sub(r"[A-ZÀ-Ý0-9][\w\-]*\s?(?:®|™)\s+(?:e|and|y|et)\s+$", "", antes)
        destino = subs if (_RE_ANTES_DE_SUBSTANCIA.search(antes)
                           or _RE_ANTES_DE_SUBSTANCIA.search(antes_sem_marcas)) else prods
        if nome not in destino:
            destino.append(nome)
    # uma marca que ja foi produto noutra frase continua produto
    subs = [s for s in subs if s not in prods]
    return {'PRODUTOS': prods, 'MARCAS_DE_SUBSTANCIA': subs}


# ── CULTURA E PROBLEMA: AS TABELAS DO CLASSIFICADOR, MAIS O QUE ELAS NAO VIAM ──
# As tabelas de `comunicacao_classificar` sao lidas de la, nunca copiadas. O que
# esta abaixo e SO o acrescimo que as 561 atividades mostraram faltar (cultura
# 213 -> 324 de 561; problema 76 -> 174). Mora aqui e nao la porque aquele
# ficheiro esta congelado pela prova da C7
# (tests/test_c7_lugar_do_fato.py · test_os_outros_dois_lugares_nao_foram_tocados):
# mudar a tabela do classificador e mudar um contrato que esta missao nao mediu
# nos POSTS-*.json dele. Quem quiser subir o acrescimo para la mede primeiro.
#
# FICARAM DE FORA de proposito: `pero` (pereira em italiano, «mas» em
# espanhol), `grano` sozinho (casa dentro de «granoturco», que e milho) e
# `mosca` (palavra corrente). Falso conhecido: «semi di soia» numa tinta.
CULTURAS_A_MAIS = {
    'TOMATO': ['pomodoro', 'pomodori', 'tomato', 'tomatoes', 'tomate'],
    'RICE': ['riso', 'risaia', 'risicoltura', 'rice'],
    'SOY': ['soia', 'soja', 'soybean', 'soybeans'],
    'SUNFLOWER': ['girasole'],
    'POME_FRUIT': ['melo', 'meleto', 'pomacee'],
    'CITRUS': ['agrumi', 'citrus'],
    'WHEAT': ['wheat', 'grano tenero'],
    'HORTICULTURE': ['orticole', 'orticoltura'],
    'MAIZE': ['corn', 'maize'],
}
PROBLEMAS_A_MAIS = {
    'WEEDS': ['infestanti', 'malerbe', 'weeds', 'weed control'],
    'POWDERY_MILDEW': ['oidio', 'powdery mildew'],
    'BOTRYTIS': ['botrite', 'botrytis'],
    'SCAB': ['ticchiolatura'],
    'APHIDS': ['afidi', 'aphids'],
    'SCALE_INSECTS': ['cocciniglia', 'cocciniglie'],
    'CORN_BORER': ['piralide'],
    'DIABROTICA': ['diabrotica'],
    'MITES': ['acari', 'ragnetto rosso'],
    'ALTERNARIA': ['alternaria'],
}


def _somar(base: dict, extra: dict) -> dict:
    fora = {k: list(v) for k, v in base.items()}
    for k, v in extra.items():
        fora.setdefault(k, [])
        fora[k] += [t for t in v if t not in fora[k]]
    return fora


CULTURAS = _somar(cl.CULTURAS, CULTURAS_A_MAIS)
PROBLEMAS = _somar(cl.PROBLEMAS, PROBLEMAS_A_MAIS)


# ── TIPO DE COMUNICACAO ──────────────────────────────────────────────────────
ANUNCIO_PAGO, ORGANICO, COMUNICADO, REGISTO = 'ANUNCIO_PAGO', 'ORGANICO', 'COMUNICADO', 'REGISTO'
_PLATAFORMAS_SOCIAIS = ('YOUTUBE', 'INSTAGRAM', 'FACEBOOK', 'LINKEDIN', 'TIKTOK', 'X', 'TWITTER')
_RE_URL_COMUNICADO = re.compile(r"/(?:comunicat[oi][-_]stampa|press[-_]?release|sala[-_]stampa|"
                                r"press|comunicati|media[-_]?room|newsroom)(?:/|$)", re.I)


def tipo_de_comunicacao(item: dict, empresa: str) -> tuple[str, str]:
    """(TIPO, BASE). Pelo que a COLETA declarou do item; o texto so decide o comunicado."""
    u = lambda k: str(item.get(k) or '').upper()  # noqa: E731
    if u('ITEM_KIND') in ('REGISTRATION', 'REGISTO') or u('TERRITORY') == 'T4':
        return REGISTO, 'o item e um registo T4 (ITEM_KIND/TERRITORY)'
    if u('ACTIVITY_TYPE') == 'PAID' or u('PLATFORM') == 'META_ADS_LIBRARY':
        return ANUNCIO_PAGO, 'ACTIVITY_TYPE=%s PLATFORM=%s' % (u('ACTIVITY_TYPE') or '-', u('PLATFORM') or '-')
    if u('ACTIVITY_TYPE').startswith('ORGANIC') or u('PLATFORM') in _PLATAFORMAS_SOCIAIS:
        return ORGANICO, 'ACTIVITY_TYPE=%s PLATFORM=%s' % (u('ACTIVITY_TYPE') or '-', u('PLATFORM') or '-')
    if u('ITEM_KIND') in ('PRESS_RELEASE', 'COMUNICADO'):
        return COMUNICADO, 'ITEM_KIND=%s' % u('ITEM_KIND')
    # Um comunicado so e da empresa se a empresa que fala e conhecida: o mesmo
    # endereco /press/ num jornal e o comunicado DO JORNAL.
    if empresa != NAO_SEI:
        if _RE_URL_COMUNICADO.search(str(item.get('URL') or item.get('AD_URL') or '')):
            return COMUNICADO, 'endereco de sala de imprensa no canal proprio da empresa'
        if re.search(r'(?<![a-z])(comunicato stampa|press release|nota de prensa|communique de presse)',
                     cl._norm(' '.join(str(item.get(k) or '') for k in ('TITLE', 'TEXT')))):
            return COMUNICADO, 'o proprio texto se declara comunicado de imprensa'
    return NAO_SEI, 'a coleta nao declarou o tipo e o texto nao o diz'


# ── ALEGACAO x FACTO ─────────────────────────────────────────────────────────
_RE_REGULATORIA = re.compile(
    r"(?<![a-z])(registrat\w*|registrazione|autorizzat\w*|autorizzazione|etichetta|"
    r"omologat\w*|decreto|ministero|uso eccezionale|deroga|n\.\s*reg|reg\.\s*n|"
    r"registered|registration|approved|authori[sz]\w*|label\b|registrad\w*|autorizad\w*)", re.I)
_RE_DESEMPENHO = re.compile(
    r"(?<![a-z])(efficac\w*|protegg\w*|protezion\w*|garantis\w*|controll\w*|riduc\w*|"
    r"miglior\w*|aument\w*|resa|qualit\w*|persistenz\w*|rapid\w*|selettiv\w*|"
    r"innovativ\w*|unic[oa]|leader|flessibil\w*|affidabil\w*|"
    r"effective|protect\w*|control\w*|yield|quality|improv\w*|eficac\w*|protege\w*)", re.I)
_RE_FRASE = re.compile(r"(?<=[.!?…])\s+|\n+")


def alegacoes(texto: str, produtos: list[str]) -> list[dict]:
    """As frases que AFIRMAM algo. Cada uma e alegacao ate prova em contrario."""
    fora = []
    for frase in _RE_FRASE.split(texto or ''):
        f = frase.strip()
        if len(f) < 8:
            continue
        tipos = []
        if _RE_REGULATORIA.search(f):
            tipos.append('ALEGACAO_REGULATORIA')
        if _RE_DESEMPENHO.search(f):
            tipos.append('ALEGACAO_DE_DESEMPENHO')
        if not tipos:
            continue
        fora.append({'FRASE': f[:400], 'TIPOS': tipos,
                     'PRODUTOS': [p for p in produtos if p in f],
                     'CAMADA': 'COMUNICACAO',
                     'ESTADO': 'ALEGACAO_ATE_PROVA_EM_CONTRARIO'})
    return fora


# ── A TOMADA DO REGISTO T4 ───────────────────────────────────────────────────
# O parser do registo italiano e de outra sessao. Aqui fica o CONTRATO do que ele
# tem de devolver, e a regra de comparar. Um registo que implemente
# `procurar_por_nome(nome) -> list[dict]` com estes campos liga-se sem mudar
# uma linha deste ficheiro.
CONTRATO_DO_REGISTO_T4 = {
    'METODO': 'procurar_por_nome(nome_observado: str) -> list[dict]',
    'CAMPOS_DE_CADA_REGISTO': ['NUMERO_REGISTRAZIONE', 'NOME_PRODOTTO', 'TITOLARE',
                               'SOSTANZE_ATTIVE', 'STATO', 'SNAPSHOT'],
    'ATRIBUTO': 'FONTE (SOURCE_ID e versao do registo lido)',
    'REGRA_DO_NOME': ('mesma chave (fontes/adama_referencia.chave) OU a marca seguida de '
                      'sufixo de formulacao («ENERVIN» casa «ENERVIN SC»)'),
}


class RegistoEmMemoria:
    """Implementacao minima do contrato — para testes e casos SINTETICOS.

    Nao e o registo italiano. Os registos que recebe dizem de onde vieram em
    `FONTE`; um teste que a use com dado inventado marca-o como sintetico.
    """

    def __init__(self, registos: list[dict], fonte: str):
        self.FONTE = fonte
        self._por_nome, self._por_marca = {}, {}
        for r in registos:
            n = str(r.get('NOME_PRODOTTO') or '')
            self._por_nome.setdefault(chave_do_nome(n), []).append(r)
            primeira = n.split()[0] if n.split() else ''
            self._por_marca.setdefault(chave_do_nome(primeira), []).append(r)

    def procurar_por_nome(self, nome: str) -> list[dict]:
        k = chave_do_nome(nome)
        if not k:
            return []
        achados = list(self._por_nome.get(k, []))
        for r in self._por_marca.get(k, []):
            if r not in achados:
                achados.append(r)
        return achados


def validar_no_registo(produto: str, empresa: str, registo) -> dict:
    """O que o registo T4 diz do nome que a empresa usou. Nunca decide venda."""
    if registo is None:
        return {'PRODUTO': produto, 'ESTADO': 'REGISTO_NAO_LIGADO', 'VALIDADO': NAO_SEI,
                'PORQUE': 'nenhum registo T4 foi entregue a esta leitura — NAO SEI, e nao «nao registado»'}
    achados = registo.procurar_por_nome(produto) or []
    fonte = getattr(registo, 'FONTE', NAO_SEI)
    if not achados:
        return {'PRODUTO': produto, 'ESTADO': 'NAO_ENCONTRADO_NO_REGISTO', 'VALIDADO': False,
                'FONTE_DO_REGISTO': fonte,
                'PORQUE': ('o nome nao casou no registo lido. Nao prova que o produto nao exista: '
                           'pode ser grafia, versao do registo, ou marca de substancia (INT-LAW-112)')}
    titulares = sorted({str(r.get('TITOLARE') or NAO_SEI) for r in achados})
    factos = [{'CAMADA': 'REGULATORIO', 'FONTE_DO_REGISTO': fonte,
               'NUMERO_REGISTRAZIONE': r.get('NUMERO_REGISTRAZIONE'),
               'NOME_PRODOTTO': r.get('NOME_PRODOTTO'), 'TITOLARE': r.get('TITOLARE'),
               'SOSTANZE_ATTIVE': r.get('SOSTANZE_ATTIVE') or [],
               'STATO': r.get('STATO') or NAO_SEI, 'SNAPSHOT': r.get('SNAPSHOT') or NAO_SEI,
               'NAO_DIZ': ['venda', 'disponibilidade comercial', 'quota de mercado']}
              for r in achados]
    if empresa == NAO_SEI:
        estado, validado = 'ENCONTRADO_EMPRESA_QUE_FALA_NAO_SEI', NAO_SEI
    else:
        do_titular = [t for t in titulares if empresa.lower() in cl._norm(t)]
        if len(do_titular) == len(titulares):
            estado, validado = 'ENCONTRADO_MESMO_TITULAR', True
        elif do_titular:
            estado, validado = 'AMBIGUO_TITULARES_DIFERENTES', NAO_SEI
        else:
            # distribuidor e titular podem ser empresas diferentes: nao e erro, e nao e prova
            estado, validado = 'ENCONTRADO_OUTRO_TITULAR', NAO_SEI
    return {'PRODUTO': produto, 'ESTADO': estado, 'VALIDADO': validado,
            'TITULARES': titulares, 'FONTE_DO_REGISTO': fonte,
            'PRODUCT_ID': (achados[0].get('NUMERO_REGISTRAZIONE') if len(achados) == 1 else NAO_SEI),
            'FACTOS_REGULATORIOS': factos}


# ── O EXTRATOR ───────────────────────────────────────────────────────────────
_CAMPOS_DE_TEXTO = ('TITLE', 'TEXT', 'CREATIVE_TEXT', 'DESCRIPTION', 'TRANSCRIPT_TEXT')
_CAMPOS_DE_DATA = (('START_DATE', 'INICIO_DA_VEICULACAO_DO_ANUNCIO'),
                   ('PUBLISHED_AT', 'PUBLICACAO'), ('DATE', 'DATA_DECLARADA_PELA_COLETA'))


def _texto(item: dict) -> str:
    return '\n'.join(str(item[k]) for k in _CAMPOS_DE_TEXTO
                     if item.get(k) and item.get(k) != cl.NAO_SEI)


def extrair(item: dict, registo=None) -> dict:
    """→ um registo da Concorrenza. Nao altera o item."""
    texto = _texto(item)
    norm = cl._norm(texto)
    empresa, base_empresa = empresa_que_fala(item)
    tipo, base_tipo = tipo_de_comunicacao(item, empresa)
    marcas = marcas_do_texto(texto)
    produtos = marcas['PRODUTOS']

    culturas = cl._achar(norm, CULTURAS)
    problemas = cl._achar(norm, PROBLEMAS)
    paises = cl._achar(norm, cl.LUGARES)
    regioes = sorted({t for t in cl.LUGARES['IT'] if t != 'italia' and cl._casa(norm, t)})

    tempo = NAO_SEI, 'a coleta nao trouxe data do item'
    for campo, base in _CAMPOS_DE_DATA:
        if item.get(campo):
            tempo = str(item[campo]), '%s (%s)' % (base, campo)
            break

    validacoes = [validar_no_registo(p, empresa, registo) for p in produtos]
    if tipo == REGISTO:
        # o item E o registo: o facto e ele mesmo, e nao ha alegacao nenhuma
        als = []
        factos = [{'CAMADA': 'REGULATORIO', 'FONTE_DO_REGISTO': item.get('SOURCE_ID', NAO_SEI),
                   'NUMERO_REGISTRAZIONE': item.get('NUMERO_REGISTRAZIONE'),
                   'NOME_PRODOTTO': item.get('NOME_PRODOTTO'), 'TITOLARE': item.get('TITOLARE'),
                   'SOSTANZE_ATTIVE': item.get('SOSTANZE_ATTIVE') or [],
                   'STATO': item.get('STATO') or NAO_SEI,
                   'NAO_DIZ': ['venda', 'disponibilidade comercial', 'quota de mercado']}]
    else:
        als = alegacoes(texto, produtos)
        factos = [f for v in validacoes for f in v.get('FACTOS_REGULATORIOS', [])]

    return {
        'EXTRATOR': EXTRATOR,
        'ID': item.get('ID') or item.get('DOCUMENT_ID') or NAO_SEI,
        'SOURCE_ID': item.get('SOURCE_ID') or NAO_SEI,
        # os nomes que o casco ja le (italy-app-model.js · competitorActivities)
        'COMPANY': empresa,
        'COMPANY_BASIS': base_empresa,
        'COMPANY_ROLE': ('ADAMA_PROPRIA' if empresa == PROPRIA.upper() else
                         'CONCORRENTE' if empresa != NAO_SEI else NAO_SEI),
        'EMPRESAS_NOMEADAS_NO_TEXTO': _empresas_em(norm),
        'PRODUCTS_PROVED': produtos,
        'PRODUCT_BASIS': 'MARCA_REGISTRADA_NO_TEXTO (® ou ™)' if produtos else NAO_SEI,
        'MARCAS_DE_SUBSTANCIA': marcas['MARCAS_DE_SUBSTANCIA'],
        'CROP_TERMS': culturas or [NAO_SEI],
        'ISSUE_TERMS': problemas or [NAO_SEI],
        'COUNTRY_OF_FACT': paises[0] if len(paises) == 1 else (paises or NAO_SEI),
        'REGION_OF_FACT': regioes or NAO_SEI,
        # alcance do anuncio viaja como veio: alcancado != dirigido, e nao e lugar do facto
        'COUNTRY_REACHED': item.get('COUNTRY_REACHED') or NAO_SEI,
        'COMMUNICATION_TIME': tempo[0],
        'COMMUNICATION_TIME_BASIS': tempo[1],
        'FACT_TIME': NAO_SEI,
        'FACT_TIME_WHY': 'a data de uma comunicacao nao e a data de um facto de campo (INT-LAW-101)',
        'TIPO_DE_COMUNICACAO': tipo,
        'TIPO_DE_COMUNICACAO_BASIS': base_tipo,
        'CLAIM_DOMAIN': 'REGULATORY_FACT' if tipo == REGISTO else 'COMPANY_CLAIM',
        'ALEGACOES': als,
        'FACTOS_REGULATORIOS': factos,
        'VALIDACAO_T4': validacoes,
        # duas contagens, nunca uma soma (CAP-COMP)
        'CONTAGEM': {'ALEGACOES': len(als), 'FACTOS_REGULATORIOS': len(factos)},
        'NUNCA_DIZ': ['venda', 'demanda', 'quota de mercado', 'investimento', 'sucesso',
                      'que o anuncio foi DIRIGIDO ao pais que alcancou'],
    }


def medir(atividades: list[dict], registo=None) -> dict:
    """Mede o extrator sobre uma lista de atividades. So le."""
    regs = [extrair(a, registo) for a in atividades]
    antes = Counter()
    for a, r in zip(atividades, regs):
        velho = set(a.get('PRODUCTS_PROVED') or [])
        novo = set(r['PRODUCTS_PROVED'])
        antes['produtos_no_pacote'] += len(velho)
        antes['produtos_aqui'] += len(novo)
        antes['marcas_de_substancia_que_o_pacote_contava_como_produto'] += len(velho & set(r['MARCAS_DE_SUBSTANCIA']))
    conta = lambda f: Counter(f(r) for r in regs)  # noqa: E731
    return {
        'EXTRATOR': EXTRATOR,
        'ITENS': len(regs),
        'POR_TIPO_DE_COMUNICACAO': dict(conta(lambda r: r['TIPO_DE_COMUNICACAO'])),
        'COM_EMPRESA': sum(1 for r in regs if r['COMPANY'] != NAO_SEI),
        'COM_PRODUTO': sum(1 for r in regs if r['PRODUCTS_PROVED']),
        'COM_CULTURA': sum(1 for r in regs if r['CROP_TERMS'] != [NAO_SEI]),
        'COM_PROBLEMA': sum(1 for r in regs if r['ISSUE_TERMS'] != [NAO_SEI]),
        'COM_PAIS_DO_FACTO': sum(1 for r in regs if r['COUNTRY_OF_FACT'] != NAO_SEI),
        'COM_DATA_DA_COMUNICACAO': sum(1 for r in regs if r['COMMUNICATION_TIME'] != NAO_SEI),
        'ALEGACOES': sum(r['CONTAGEM']['ALEGACOES'] for r in regs),
        'FACTOS_REGULATORIOS': sum(r['CONTAGEM']['FACTOS_REGULATORIOS'] for r in regs),
        'PRODUTOS_COMPARADOS_COM_O_PACOTE': dict(antes),
        'CINCO_PRODUTOS_MAIS_CITADOS': Counter(p for r in regs for p in r['PRODUCTS_PROVED']).most_common(5),
        'MARCAS_DE_SUBSTANCIA': dict(Counter(s for r in regs for s in r['MARCAS_DE_SUBSTANCIA'])),
    }


FONTE_DO_REPO = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2', 'PREVIOUS-HANDOFF',
                             '01-DESIGN-READY', 'COMPETITOR-WATCH', 'competitor-activities.json')

if __name__ == '__main__':
    with open(FONTE_DO_REPO, encoding='utf-8') as f:
        atividades = json.load(f)['ACTIVITIES']
    print(json.dumps(medir(atividades), ensure_ascii=False, indent=1))
