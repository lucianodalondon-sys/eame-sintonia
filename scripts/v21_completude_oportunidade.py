#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A MEDIDA DA COMPLETUDE - o que cada oportunidade DEIXOU DE OLHAR.

    python3 scripts/v21_completude_oportunidade.py

POR QUE ESTE ARQUIVO EXISTE
---------------------------
Chegou um relato: uma oportunidade de VITE mostrava UM produto ADAMA, havendo
varios. A pergunta nao e <<o relato e verdade?>> - e <<quanto do acervo cada
oportunidade chegou a consultar antes de decidir?>>.

    NAO SE MEDE UMA ESCOLHA PELO QUE ELA MOSTROU.
    MEDE-SE PELO QUE ELA TINHA PARA OLHAR.

Este arquivo nao decide, nao promove e nao rebaixa nada. Ele CONTA duas coisas,
para cada oportunidade do pacote servido:

  A - COMPLETUDE DE PORTFOLIO
      quantos produtos ADAMA existem no acervo para aquela cultura, quantos a
      oportunidade enxergou, e quais ficaram de fora. A conta tem de fechar:
          ENCONTRADOS = LIGADOS + NAO_LIGADOS + NAO_SEI
      Cada produto que sobra sem classe e uma falha, nao um detalhe.

  B - COMPLETUDE DE CRUZAMENTO
      cada familia de inteligencia do acervo e cruzada com o fato especifico da
      oportunidade - cultura x alvo x regiao. Uma familia sem correspondencia
      devolve NAO_ENCONTRADO, que e resultado; nunca ligacao inventada.

O TERCEIRO ESTADO, QUE NAO E ZERO
---------------------------------
Ha material que existe e nao serve: 1.115 videos coletados, 48 transcricoes
pedidas, uma unica com texto. Contar isso como zero mente sobre o acervo;
contar como match mente sobre a evidencia. Fica MATERIAL_EXISTENTE_NAO_UTILIZAVEL,
com o motivo escrito ao lado.

    O QUE EXISTE E NAO SERVE NAO E AUSENCIA: E DIVIDA COM ENDERECO.

DE ONDE LE
----------
Do pacote SERVIDO - `italia-portale/client/italy-handoff-v21.js` - porque a
pergunta e sobre o que a tela mostra hoje, e nao sobre o que uma cadeia noutra
linhagem produziria. O acervo que nao entrou no pacote (o censo do catalogo
ADAMA, o corpus de video do SENSOR-PILOT) entra direto de `data/samples/`.
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, 'italia-portale', 'client')
PORTAL = os.path.join(CLI, 'italy-handoff-v21.js')
SNAPSHOT = os.path.join(CLI, 'meeting-intelligence-snapshot.json')
CASA = os.path.join(CLI, 'italy-casa.js')
SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'IT-COMPLETUDE')

NUL = chr(0)


# -- O FUNIL, CONTADO EM CADA DEGRAU -----------------------------------------
# Entre o acervo e o ecra ha QUATRO reducoes, e nenhuma delas se ve de dentro
# da seguinte. Contar so a ultima faz o portfolio parecer pequeno; contar so a
# primeira faz o motor parecer completo. Contam-se as quatro.
#
#     UMA PERDA QUE SO APARECE NO DEGRAU SEGUINTE NAO E PERDA MEDIDA:
#     E PERDA HERDADA.
def le_snapshot():
    return json.load(open(SNAPSHOT, encoding='utf-8'))


def le_casa():
    s = open(CASA, encoding='utf-8').read()
    i = s.index('window.ITALY_CASA = ')
    return json.loads(s[i + len('window.ITALY_CASA = '):].rstrip().rstrip(';'))


# -- O PACOTE SERVIDO, LIDO SEM NAVEGADOR ------------------------------------
# O ficheiro e JS com um pool de strings: NUL+"123" e P[123]. Um leitor que
# precise de Node para abrir o pacote nao serve a uma medicao que tem de correr
# em qualquer maquina. Entao le-se aqui, com json e uma substituicao.
def le_pacote():
    s = open(PORTAL, encoding='utf-8').read()
    i = s.index('var P = [')
    j = s.index('];', i)
    pool = json.loads(s[i + len('var P = '):j + 1])
    k = s.index('window.ITALY_HANDOFF_V21 = R(')
    corpo = s[k + len('window.ITALY_HANDOFF_V21 = R('):s.rindex('});') + 1]
    dados = json.loads(corpo)

    def R(v):
        if isinstance(v, str):
            return pool[int(v[1:])] if v[:1] == NUL else v
        if isinstance(v, list):
            return [R(x) for x in v]
        if isinstance(v, dict):
            return {k2: R(v2) for k2, v2 in v.items()}
        return v
    return R(dados)


# -- AS FAMILIAS, E POR QUE CHAVE CADA UMA SE DEIXA CRUZAR -------------------
# A chave e o nome da familia; o valor diz de onde ela vem no pacote servido e
# por que campos ela se deixa cruzar.
#
#     FAMILIA QUE NAO SE DEIXA CRUZAR POR NENHUM CAMPO NAO E FAMILIA CEGA:
#     E FAMILIA SEM CHAVE, E ISSO TAMBEM E UMA MEDIDA.
FAMILIAS = {
    'PRODUTO_ADAMA_ROTULO':    ('productRelationships',   ('crop', 'issue')),
    'PORTFOLIO_COMERCIAL':     ('productsCommercial',     ('crop',)),
    'REGISTRO_ROTULO':         ('productsRegulatory',     ('crop',)),
    'SUBSTANCIA_ATIVA':        ('activeIngredients',      ('sem_chave',)),
    'SINAL_DE_CAMPO':          ('fieldBulletins',         ('crop', 'issue', 'region')),
    'JANELA_DE_CULTURA':       ('currentFieldSignals',    ('crop', 'issue', 'region')),
    'CLIMA':                   ('agrometConditions',      ('crop', 'region')),
    'CIENCIA':                 ('scienceRecords',         ('crop', 'issue')),
    'PESQUISADORES':           ('researchers',            ('tema',)),
    'VOZES_PUBLICAS':          ('publicVoices',           ('crop', 'issue')),
    'CANAIS_CREATORS':         ('publicChannels',         ('tema',)),
    'CONCORRENCIA':            ('competitorActivities',   ('crop', 'issue')),
    'REGULATORIO':             ('regulatoryFutureFacts',  ('crop',)),
    'REGULATORIO_FUTURO':      ('regulatoryFuture',       ('crop',)),
    'EVENTOS':                 ('events',                 ('crop', 'region')),
    'EVENTOS_FUTUROS':         ('futureEvents',           ('crop', 'region')),
    'MERCADO':                 ('marketObservations',     ('crop',)),
    'PESO_ECONOMICO_HISTORICO': ('cropEconomics',         ('crop', 'region')),
    'RESISTENCIA':             ('resistance',             ('crop', 'issue')),
    'NOTICIAS':                ('news',                   ('crop',)),
    'SINAL_FUTURO':            ('futureSignals',          ('crop',)),
    'RELACOES':                ('relationships',          ('sem_chave',)),
    'CRUZAMENTOS_CLIENT_SAFE': ('clientSafeCrossings',    ('sem_chave',)),
}

# Familias que existem no acervo e NUNCA foram ingeridas no pacote.
FAMILIAS_FORA_DO_PACOTE = ('VIDEOS', 'TRANSCRICOES', 'COMENTARIOS_DE_VIDEO',
                           'CATALOGO_ADAMA_CENSO')


# -- O QUE O MOTOR REALMENTE CARREGA ----------------------------------------
# Lido de scripts/v21_oportunidades.py, nao decorado: a lista esta la em main().
# Ler em vez de copiar e o que impede esta medicao de envelhecer em silencio.
def familias_que_o_motor_carrega():
    src = open(os.path.join(ROOT, 'scripts', 'v21_oportunidades.py'),
               encoding='utf-8').read()
    m = re.search(r"C = \{n: _le\(n \+ '\.json'\) for n in \((.*?)\)\}", src, re.S)
    carregadas = set(re.findall(r"'([A-Z0-9-]+)'", m.group(1))) if m else set()
    # CARREGAR NAO E USAR. Uma colecao que entra no dicionario e nunca mais e
    # referida foi lida do disco e deitada fora - e o efeito, na tela, e o
    # mesmo de nunca ter sido lida.
    usadas = set()
    for nome in carregadas:
        if len(re.findall(r"cs\['%s'\]" % re.escape(nome), src)) > 0:
            usadas.add(nome)
    return carregadas, usadas


# -- O CORPUS DE VIDEO, QUE NUNCA ENTROU NO PACOTE --------------------------
def le_video():
    def _itens(padrao):
        out = []
        for f in sorted(glob.glob(os.path.join(SAMPLES, 'SENSOR-PILOT', padrao))):
            out += json.load(open(f, encoding='utf-8')).get('ITEMS', [])
        return out
    return _itens('VIDEOS-*.json'), _itens('TRANSCRICOES-*.json'), _itens('COMENTARIOS-*.json')


def le_censo_catalogo():
    p = os.path.join(SAMPLES, 'IT-CATALOGO', 'IT-ADAMA-CATALOG-CENSUS-2026-09-02.json')
    return json.load(open(p, encoding='utf-8')).get('PRODUCTS', [])


# -- A PONTE DE VOCABULARIO, DECLARADA E NAO ADIVINHADA ---------------------
# O corpus de video escreve VINE; o pacote escreve CROP_GRAPEVINE. O censo do
# catalogo escreve <<Vite da vino>> e <<Vite da tavola>>; o rotulo ministerial
# escreve VITE. Sao TRES grafias da mesma cultura, e nenhuma tabela as unia.
#
#     DUAS GRAFIAS SEM PONTE NAO SAO DUAS CULTURAS: SAO UMA CULTURA PERDIDA.
#
# Esta tabela nao normaliza nada no pacote: ela so permite MEDIR o que a falta
# de normalizacao esconde.
VIDEO_CROP = {
    'VINE': 'CROP_GRAPEVINE', 'OLIVE': 'CROP_OLIVE', 'MAIZE': 'CROP_MAIZE',
    'SOYBEAN': 'CROP_SOYBEAN', 'SUGARBEET': 'CROP_SUGAR_BEET', 'RICE': 'CROP_RICE',
    'APPLE': 'CROP_APPLE', 'TOMATO': 'CROP_TOMATO', 'CEREAL': 'CROP_WHEAT_GENERIC',
    'DURUM_WHEAT': 'CROP_DURUM_WHEAT',
}
# WEED, DISEASE e INSECT sao GUARDA-CHUVAS, nao alvos: <<disease>> nao e
# ticchiolatura. Mapea-los para um ISSUE_ concreto seria fabricar precisao que
# a consulta de origem nunca teve. Ficam None de proposito.
VIDEO_ISSUE = {
    'DOWNY_MILDEW': 'ISSUE_DOWNY_MILDEW', 'SEPTORIA': 'ISSUE_SEPTORIA',
    'FUSARIUM': 'ISSUE_FUSARIUM', 'AMARANTHUS': 'ISSUE_AMARANTHUS',
    'BACTROCERA': 'ISSUE_BACTROCERA', 'FLAVESCENCE': 'ISSUE_SCAPHOIDEUS',
    'REPILO': 'ISSUE_REPILO', 'WEED': None, 'DISEASE': None, 'INSECT': None,
}
CATALOGO_CROP = {
    'vite da vino': 'CROP_GRAPEVINE', 'vite da tavola': 'CROP_GRAPEVINE',
    'melo': 'CROP_APPLE', 'pomodoro': 'CROP_TOMATO', 'mais': 'CROP_MAIZE',
    'mais dolce': 'CROP_MAIZE', 'mais da foraggio': 'CROP_MAIZE',
    'riso': 'CROP_RICE', 'soia': 'CROP_SOYBEAN', 'orzo': 'CROP_BARLEY',
    'frumento': 'CROP_WHEAT_GENERIC', 'cereali': 'CROP_WHEAT_GENERIC',
    'barbabietola da zucchero': 'CROP_SUGAR_BEET', 'olivo': 'CROP_OLIVE',
    'pero': 'CROP_PEAR', 'pesco': 'CROP_PEACH', 'patata': 'CROP_POTATO',
    'actinidia': 'CROP_KIWI', 'girasole': 'CROP_SUNFLOWER',
    'ciliegio': 'CROP_STONE_FRUIT', 'albicocco': 'CROP_STONE_FRUIT',
    'arancio': 'CROP_CITRUS', 'limone': 'CROP_CITRUS',
    'mandarino': 'CROP_CITRUS', 'clementino': 'CROP_CITRUS',
    'pomacee': 'CROP_APPLE',
}
# Palavra que liga um tema de pesquisador/canal a uma cultura. NAO e ligacao de
# evidencia: e a PENEIRA que diz onde vale a pena olhar. Quem liga e o humano,
# e por isso todo match por esta via nasce marcado TRIAGEM_POR_TEMA.
TEMA_CROP = {
    'CROP_GRAPEVINE': ('vite', 'vine', 'grape', 'vitis', 'uva', 'wine', 'viticolt'),
    'CROP_OLIVE': ('oliv', 'olea'),
    'CROP_MAIZE': ('mais', 'maize', 'corn', 'zea mays'),
    'CROP_WHEAT_GENERIC': ('frumento', 'wheat', 'cereal', 'triticum'),
    'CROP_DURUM_WHEAT': ('durum', 'grano duro'),
    'CROP_TOMATO': ('pomodoro', 'tomato', 'solanum lyco'),
    'CROP_RICE': ('riso', 'rice', 'oryza'),
    'CROP_APPLE': ('melo', 'apple', 'malus'),
    'CROP_SOYBEAN': ('soia', 'soy', 'glycine'),
    'CROP_SUGAR_BEET': ('barbabietola', 'beet', 'beta vulgaris'),
    'CROP_BARLEY': ('orzo', 'barley', 'hordeum'),
    'CROP_CITRUS': ('agrum', 'citrus'),
    'CROP_PEAR': ('pero', 'pear', 'pyrus'),
    'CROP_VEGETABLES': ('ortagg', 'vegetable', 'orticol'),
}


def _num(x):
    return re.sub(r'\D', '', str(x or '')).lstrip('0').zfill(6)


def _entrada_do_arquetipo(o, rot_por_crop, rot_por_par, pkg):
    """Quantos produtos o arquetipo POS na mao de `emitir`, antes do corte.

    Isolar o corte exige reconstruir o que entrou nele. Cada arquetipo tem um
    recorte proprio, e nenhum e errado — sao perguntas diferentes:

      O1, O3   o par cultura x alvo. A pergunta e sobre um problema observado.
      O2, O4, O6  a cultura inteira. A pergunta e sobre a cultura, sem alvo.
      O5       os produtos que contem a SUBSTANCIA que expira, venham da
               cultura que vierem. A pergunta e de portfolio e de supply.

        CONFUNDIR O RECORTE COM A PERDA E CULPAR O ARQUETIPO POR RESPONDER
        A PERGUNTA QUE LHE FOI FEITA.
    """
    arq, crop, alvo = o.get('ARCHETYPE'), o.get('CROP'), o.get('TARGET')
    if arq in ('O1_FIELD_PRESSURE', 'O3_RESISTANCE_MOA'):
        return len(rot_por_par.get((crop, alvo), set())) if (crop and alvo) else None
    if arq in ('O2_MARKET_MOMENT', 'O4_COMPETITIVE_OPENING', 'O6_SCIENCE_TO_FIELD'):
        return len(rot_por_crop.get(crop, set())) if crop else None
    if arq == 'O5_REGULATORY_PREPARATION':
        # O cartao nao guarda de que substancia nasceu, entao procura-se o fato
        # regulatorio cujo conjunto de produtos CONTEM o que o cartao mostra —
        # e, havendo mais de um, o menor. Nao havendo nenhum, e NAO SEI, e fica
        # None: inventar aqui seria fabricar o denominador da propria acusacao.
        reg = {_num(p.get('REGISTRATION_NUMBER')): p
               for p in pkg.get('productsRegulatory', []) if p.get('CLIENT_SAFE')}
        mostrados = set(o.get('PRODUCT_RELATIONSHIPS') or [])
        melhor = None
        for f in pkg.get('regulatoryFutureFacts', []):
            if not f.get('CLIENT_SAFE'):
                continue
            nomes = {reg[_num(x)].get('NAME')
                     for x in (f.get('ITALIAN_REGISTRATIONS') or [])
                     if _num(x) in reg}
            nomes.discard(None)
            if nomes and mostrados <= nomes and (melhor is None or len(nomes) < melhor):
                melhor = len(nomes)
        return melhor
    return None


def _lista(r, campo):
    v = r.get(campo)
    return v if isinstance(v, list) else ([] if v is None else [v])


def _texto(r):
    return ' '.join(str(r.get(k) or '') for k in
                    ('THEME', 'NAME', 'TITLE', 'CHANNEL', 'CROP', 'ISSUE',
                     'CROP_TERMS', 'ISSUE_TERMS', 'CROP_LITERAL', 'SUBJECT',
                     'DESCRIPTION', 'CROP_DECLARED')).lower()


def cruza(regs, chaves, crop, alvo, geo):
    """Devolve (match_forte, match_cultura, motivo) para uma familia.

    match_forte  - o registro nomeia a cultura E o alvo do caso (ou a regiao,
                   quando a familia nao tem alvo). E a ligacao defensavel.
    match_cultura - o registro nomeia a cultura, e nada mais. Vale como
                   contexto, nunca como prova do caso.

        CULTURA IGUAL NAO E O MESMO FATO.
        UM FUNGICIDA DE VITE NAO PROVA NADA SOBRE A FLAVESCENCIA.
    """
    if 'sem_chave' in chaves:
        return [], [], 'familia sem chave de cultura: nao se deixa cruzar por caso'
    forte, cultura = [], []
    for r in regs:
        crops = _lista(r, 'CROP_IDS')
        issues = _lista(r, 'ISSUE_IDS')
        regions = _lista(r, 'REGION_IDS')
        bate_crop = crop in crops
        if not bate_crop and 'tema' in chaves and crop:
            bate_crop = any(t in _texto(r) for t in TEMA_CROP.get(crop, ()))
        if not bate_crop:
            continue
        cultura.append(r)
        bate_alvo = bool(alvo) and alvo in issues
        bate_geo = bool(geo) and (geo in regions or 'GEO_ITALY' in regions)
        if ('issue' in chaves and bate_alvo) or \
           ('issue' not in chaves and 'region' in chaves and bate_geo):
            forte.append(r)
    return forte, cultura, ''


def main():
    pkg = le_pacote()
    ops = pkg['opportunities']
    videos, transcricoes, comentarios = le_video()
    censo = le_censo_catalogo()
    carregadas, usadas = familias_que_o_motor_carrega()
    snap = {c['ID']: c for c in le_snapshot().get('CASES', [])}
    casa = {c['ID']: c for c in le_casa()['OPPORTUNITA_ATTUALI']['CASI']}

    # -- O UNIVERSO ADAMA POR CULTURA, DAS TRES CASAS QUE O GUARDAM ---------
    # O motor so conhece a primeira. As outras duas existem, estao versionadas
    # e nunca foram perguntadas.
    # ⚠️ O MOTOR SO VE O QUE PASSA NO PORTAO CLIENT_SAFE.
    # `cs = {k: [x for x in v if x.get('CLIENT_SAFE')] ...}` em
    # v21_oportunidades.main(). Das 2.030 duplas de rotulo, 1.512 sao
    # client-safe: 518 nunca chegam ao motor. Medir o universo sem este filtro
    # acusa o motor de nao ter olhado para o que ele nao podia ver.
    #
    #     UM DENOMINADOR MAIOR QUE O QUE O MOTOR RECEBE NAO MEDE O MOTOR:
    #     MEDE A DISTANCIA ATE UM MOTOR QUE NAO EXISTE.
    #
    # Entao contam-se OS DOIS: o acervo inteiro (o que existe) e o que o portao
    # deixa passar (o que o motor pode olhar). A diferenca tem nome proprio.
    def _cs(col):
        return [x for x in pkg.get(col, []) if x.get('CLIENT_SAFE')]

    rot_por_crop = defaultdict(set)          # rotulo ministerial, CLIENT_SAFE
    rot_por_par = defaultdict(set)           # rotulo CLIENT_SAFE, cultura x alvo
    rot_todos_por_crop = defaultdict(set)    # rotulo inteiro, sem portao
    for r in pkg['productRelationships']:
        for c in _lista(r, 'CROP_IDS'):
            if not r.get('PRODUCT_NAME'):
                continue
            rot_todos_por_crop[c].add(r['PRODUCT_NAME'])
            if not r.get('CLIENT_SAFE'):
                continue
            rot_por_crop[c].add(r['PRODUCT_NAME'])
            for i in _lista(r, 'ISSUE_IDS'):
                rot_por_par[(c, i)].add(r['PRODUCT_NAME'])
    com_por_crop = defaultdict(set)          # catalogo comercial, ja no pacote
    for p in pkg['productsCommercial']:
        for c in _lista(p, 'CROP_IDS'):
            com_por_crop[c].add(p.get('NAME'))
    # A QUARTA CASA. O registo ministerial das 163 autorizacoes ADAMA e
    # portfolio tanto quanto o catalogo - e e por ele que o arquetipo O5
    # escolhe produto. Deixa-lo fora da conta faria aparecer como <<produto sem
    # lastro>> exactamente aquilo que o motor foi buscar ao sitio certo.
    #
    #     UMA CONTA QUE NAO CONHECE UMA DAS CASAS ACUSA A CASA, NAO O ERRO.
    reg_por_crop = defaultdict(set)
    for p in pkg['productsRegulatory']:
        for c in _lista(p, 'CROP_IDS'):
            reg_por_crop[c].add(p.get('NAME'))
    cen_por_crop = defaultdict(set)          # censo do catalogo, FORA do pacote
    for p in censo:
        for lit in (p.get('CROPS_DECLARED_ON_PAGE') or []):
            cid = CATALOGO_CROP.get(str(lit).strip().lower())
            if cid:
                cen_por_crop[cid].add(p.get('NAME'))

    def nome(n):
        """O nome comercial e o mesmo produto escrito de tres maneiras.
        FOLPAN GOLD, Folpan(R) Gold e folpan gold sao um produto so."""
        return re.sub(r'[^A-Z0-9]', '', str(n or '').upper().replace('®', ''))

    vid_por_crop = defaultdict(list)
    for v in videos:
        cid = VIDEO_CROP.get(v.get('CROP'))
        if cid:
            vid_por_crop[cid].append(v)

    fichas = []
    for o in sorted(ops, key=lambda x: x['ID']):
        crop, alvo, geo = o.get('CROP'), o.get('TARGET'), o.get('GEOGRAPHY')
        mostrados = o.get('PRODUCT_RELATIONSHIPS') or []

        # ---- A - PORTFOLIO -------------------------------------------------
        univ_rot = rot_por_crop.get(crop, set())
        univ_com = com_por_crop.get(crop, set())
        univ_cen = cen_por_crop.get(crop, set())
        univ_reg = reg_por_crop.get(crop, set())
        univ_nomes = {}
        for fonte, conj in (('ROTULO', univ_rot), ('CATALOGO_NO_PACOTE', univ_com),
                            ('CENSO_FORA_DO_PACOTE', univ_cen),
                            ('REGISTO_MINISTERIAL', univ_reg)):
            for n in conj:
                univ_nomes.setdefault(nome(n), {'nome': n, 'fontes': []})
                univ_nomes[nome(n)]['fontes'].append(fonte)
        vistos = {nome(n) for n in mostrados}
        # o que o rotulo autoriza para o PAR do caso - so isto pode ser
        # LIGADO sem leitura humana; o resto e candidato.
        do_par = {nome(n) for n in rot_por_par.get((crop, alvo), set())} if alvo else set()

        fora = []
        for k, v in sorted(univ_nomes.items()):
            if k in vistos:
                continue
            fora.append({
                'PRODUTO': v['nome'],
                'FONTES': sorted(set(v['fontes'])),
                'AUTORIZADO_NO_PAR_DO_CASO': k in do_par,
                # A classe C nasce aqui e e o resultado honesto: o produto
                # existe para a cultura, e nada no acervo diz se serve ao fato.
                'CLASSE_AUTOMATICA': ('B_NAO_LIGADO' if alvo and k not in do_par
                                      else 'C_NAO_SEI'),
                'MOTIVO': ('o rotulo nao nomeia este produto para o alvo do caso'
                           if alvo and k not in do_par else
                           'sem alvo declarado no caso: nada permite aceitar nem rejeitar'),
            })
        # Um produto MOSTRADO que nao aparece em nenhuma das tres casas e uma
        # ligacao sem lastro - e a falha mais grave que esta conta pode achar.
        orfaos = [n for n in mostrados if nome(n) not in univ_nomes]

        # ---- B - CRUZAMENTO ------------------------------------------------
        familias = {}
        for fam, (col, chaves) in FAMILIAS.items():
            regs = [r for r in pkg.get(col, []) if isinstance(r, dict)]
            forte, cult, motivo = cruza(regs, chaves, crop, alvo, geo)
            familias[fam] = {
                'CONSULTADA': True,
                'MOTOR_CONSULTA': col in _COL2ING and _COL2ING[col] in usadas,
                'MATCH_FORTE': len(forte),
                'MATCH_SO_CULTURA': len(cult),
                'RESULTADO': ('MATCH' if forte else
                              ('MATCH_SO_CULTURA' if cult else 'NAO_ENCONTRADO')),
                'EVIDENCIAS': [r.get('ID') for r in forte[:12] if r.get('ID')],
                'NOTA': motivo,
            }
        # As familias de fora do pacote entram medidas pela mesma regua.
        vids = vid_por_crop.get(crop, [])
        vids_alvo = [v for v in vids if VIDEO_ISSUE.get(v.get('ISSUE')) == alvo] if alvo else []
        familias['VIDEOS'] = {
            'CONSULTADA': True, 'MOTOR_CONSULTA': False,
            'MATCH_FORTE': len(vids_alvo), 'MATCH_SO_CULTURA': len(vids),
            'RESULTADO': ('MATERIAL_EXISTENTE_NAO_UTILIZAVEL' if vids else 'NAO_ENCONTRADO'),
            'EVIDENCIAS': [v.get('EXTERNAL_ID') for v in (vids_alvo or vids)[:12]],
            'NOTA': ('corpus de video existe e nunca foi ingerido no pacote; '
                     'CROP_ISSUE_BASIS diz "declarado pela consulta, nao lido do '
                     'titulo" - o par vem do termo de busca, nao do conteudo'),
        }
        com_texto = [t for t in transcricoes
                     if str(t.get('TRANSCRIPT') or 'None') not in ('None', '')]
        familias['TRANSCRICOES'] = {
            'CONSULTADA': True, 'MOTOR_CONSULTA': False,
            'MATCH_FORTE': 0, 'MATCH_SO_CULTURA': 0,
            'RESULTADO': 'MATERIAL_EXISTENTE_NAO_UTILIZAVEL',
            'EVIDENCIAS': [],
            'NOTA': ('%d transcricoes pedidas, %d com texto: as restantes sao '
                     'REQUESTED_EMPTY, um estado, nao ausencia'
                     % (len(transcricoes), len(com_texto))),
        }
        familias['CATALOGO_ADAMA_CENSO'] = {
            'CONSULTADA': True, 'MOTOR_CONSULTA': False,
            'MATCH_FORTE': len(univ_cen), 'MATCH_SO_CULTURA': len(univ_cen),
            'RESULTADO': 'MATCH' if univ_cen else 'NAO_ENCONTRADO',
            'EVIDENCIAS': sorted(univ_cen)[:12],
            'NOTA': 'censo publico do catalogo ADAMA; grafia <<Vite da vino>> / <<Vite da tavola>>',
        }

        encontrados = len(univ_nomes)
        ligados = len([k for k in vistos if k in univ_nomes])
        classes = Counter(f['CLASSE_AUTOMATICA'] for f in fora)
        fecha = encontrados == ligados + classes['B_NAO_LIGADO'] + classes['C_NAO_SEI']

        # ---- O FUNIL, DEGRAU A DEGRAU, CADA PERDA COM O SEU DONO -----------
        # A primeira versao desta conta tinha UM degrau chamado
        # PERDIDO_PELO_CORTE_12 e ele media `universo - mostrados` — o que
        # empilha tres mecanismos diferentes num nome so e culpa o corte por
        # perdas que nao sao dele. Medido: dos 184 que aquele campo somava, so
        # 81 saem do corte; o resto e o portao CLIENT_SAFE e o RECORTE DO
        # ARQUETIPO (O5 escolhe por substancia, nao por cultura).
        #
        #     UMA PERDA SEM DONO ACUSA O SUSPEITO MAIS VISIVEL.
        #     CADA DEGRAU RESPONDE PELO SEU, OU A CONTA NAO ENSINA NADA.
        #
        # 1 ACERVO     tudo o que as quatro casas tem para a cultura
        # 2 PORTAO     o que CLIENT_SAFE deixa o motor ver
        # 3 ARQUETIPO  o que o arquetipo escolhe olhar (o par, a cultura, ou a
        #              substancia — sao recortes diferentes e legitimos)
        # 4 CORTE      o que sobra depois de produtos[:12]
        # 5 CATALOGO   o que casa com o catalogo comercial por numero de registo
        s = snap.get(o['ID']) or {}
        k = casa.get(o['ID']) or {}
        entrada = _entrada_do_arquetipo(o, rot_por_crop, rot_por_par, pkg)
        no_par = len(rot_por_par.get((crop, alvo), set())) if alvo else len(univ_rot)
        pm = len(s.get('PORTFOLIO_MATCHES') or [])
        funil = {
            '1_ACERVO_QUATRO_CASAS': encontrados,
            '2_ROTULO_INTEIRO_DA_CULTURA': len(rot_todos_por_crop.get(crop, set())),
            '3_ROTULO_APOS_PORTAO_CLIENT_SAFE': len(univ_rot),
            '4_ENTRADA_DO_ARQUETIPO': entrada,
            '5_APOS_CORTE_12': len(mostrados),
            '6_APOS_CASAR_COM_CATALOGO': pm,
            'ROTULO_NO_PAR_DO_CASO': no_par,
            'PERDIDO_PELO_PORTAO_CLIENT_SAFE':
                len(rot_todos_por_crop.get(crop, set())) - len(univ_rot),
            'PERDIDO_PELO_CORTE_12': (max(0, entrada - 12)
                                      if entrada is not None else None),
            'PERDIDO_AO_CASAR_COM_CATALOGO': len(mostrados) - pm,
            'RAZAO_DO_PRINCIPAL': s.get('PRIMARY_MATCH_REASON'),
            # DUAS TELAS VIVAS, DUAS LISTAS DIFERENTES. casa.html mostra
            # PORTFOLIO_MATCHES; portale.html cai em PRODUCT_RELATIONSHIPS
            # (italy-app-model.js:3802 -> portale.html:3184). O mesmo cartao tem
            # dois numeros de produto conforme a porta por onde se entra.
            'NO_ECRA_CASA': len(k.get('PRODOTTI') or []),
            'NO_ECRA_PORTALE': len(mostrados),
            'AS_DUAS_TELAS_DIVERGEM': len(k.get('PRODOTTI') or []) != len(mostrados),
            'VALIDACOES_NO_ECRA': sorted({p.get('VALIDAZIONE')
                                          for p in (k.get('PRODOTTI') or [])}),
        }

        fichas.append({
            'ID': o['ID'], 'ARQUETIPO': o.get('ARCHETYPE'), 'CULTURA': crop,
            'ALVO': alvo, 'GEOGRAFIA': geo,
            'ESTADO': o.get('OPPORTUNITY_STATE'),
            'FUNIL': funil,
            'PORTFOLIO': {
                'PRODUTOS_ADAMA_ENCONTRADOS': encontrados,
                'LIGADOS': ligados,
                'NAO_LIGADOS': classes['B_NAO_LIGADO'],
                'NAO_SEI': classes['C_NAO_SEI'],
                'CONTA_FECHA': fecha,
                'MOSTRADOS_PELA_OPORTUNIDADE': mostrados,
                'MOSTRADOS_SEM_LASTRO': orfaos,
                'FICARAM_DE_FORA': fora,
                'UNIVERSO_POR_FONTE': {
                    'ROTULO_MINISTERIAL': len(univ_rot),
                    'CATALOGO_NO_PACOTE': len(univ_com),
                    'CENSO_FORA_DO_PACOTE': len(univ_cen),
                    'REGISTO_MINISTERIAL': len(univ_reg),
                },
            },
            'CRUZAMENTO': familias,
            'FAMILIAS_CONSULTADAS': len(familias),
            'FAMILIAS_COM_MATCH': sum(1 for f in familias.values()
                                      if f['RESULTADO'] == 'MATCH'),
            'FAMILIAS_SEM_RESULTADO': sorted(k for k, f in familias.items()
                                             if f['RESULTADO'] == 'NAO_ENCONTRADO'),
            'FAMILIAS_MATERIAL_NAO_UTILIZAVEL': sorted(
                k for k, f in familias.items()
                if f['RESULTADO'] == 'MATERIAL_EXISTENTE_NAO_UTILIZAVEL'),
            'FAMILIAS_QUE_O_MOTOR_NAO_CONSULTA': sorted(
                k for k, f in familias.items() if not f['MOTOR_CONSULTA']),
        })

    # -- OS DOIS CASOS-TESTEMUNHA -------------------------------------------
    # VITE porque o relato apontou para la. MAIS porque o acervo de
    # concorrencia esta cheio dele - e volume de anuncio nao e necessidade
    # agronomica, o que so se prova pondo o denominador ao lado.
    #
    #     SETENTA ANUNCIOS DE MILHO SOBRE 577 PECAS SAO UM NUMERO.
    #     SOBRE 156 PECAS COM CULTURA DECLARADA SAO OUTRO.
    #     E DOIS ATIVOS HOJE SAO UM TERCEIRO. OS TRES TEM DE APARECER.
    def testemunha(crop, alvos_do_caso):
        u_rot, u_com = rot_por_crop.get(crop, set()), com_por_crop.get(crop, set())
        u_cen, u_reg = cen_por_crop.get(crop, set()), reg_por_crop.get(crop, set())
        uni = {}
        for f, s in (('ROTULO', u_rot), ('CATALOGO_NO_PACOTE', u_com),
                     ('CENSO_DA_FICHA', u_cen), ('REGISTO_MINISTERIAL', u_reg)):
            for n in s:
                uni.setdefault(nome(n), {'PRODUTO': n, 'FONTES': set()})['FONTES'].add(f)
        comp = [a for a in pkg['competitorActivities'] if crop in _lista(a, 'CROP_IDS')]
        comp_cult = Counter(c for a in pkg['competitorActivities']
                            for c in _lista(a, 'CROP_IDS'))
        sinais = [r for r in pkg['fieldBulletins'] if crop in _lista(r, 'CROP_IDS')]
        janelas = [w for w in pkg['currentFieldSignals'] if crop in _lista(w, 'CROP_IDS')]
        return {
            'CULTURA': crop,
            'PRODUTOS_TOTAL': len(uni),
            'PRODUTOS': sorted((v['PRODUTO'], sorted(v['FONTES'])) for v in uni.values()),
            'POR_FONTE': {'ROTULO': len(u_rot), 'CATALOGO_NO_PACOTE': len(u_com),
                          'CENSO_DA_FICHA': len(u_cen), 'REGISTO_MINISTERIAL': len(u_reg)},
            'LIGADOS_POR_ALVO': {a: sorted(rot_por_par.get((crop, a), set()))
                                 for a in alvos_do_caso},
            'CONCORRENCIA': {
                'PECAS': len(comp),
                'DENOMINADOR_PECAS_COM_CULTURA': sum(comp_cult.values()),
                'DENOMINADOR_CORPUS_INTEIRO': len(pkg['competitorActivities']),
                'PECAS_SEM_CULTURA_DECLARADA': sum(
                    1 for a in pkg['competitorActivities'] if not _lista(a, 'CROP_IDS')),
                'ATIVAS_AGORA': sum(1 for a in comp if a.get('ACTIVE_STATUS') == 'ACTIVE'),
                'ANUNCIANTES': dict(Counter(a.get('COMPANY') or 'NAO_DECLARADO'
                                            for a in comp)),
                'PRODUTOS_PROVADOS': dict(Counter(
                    p for a in comp for p in _lista(a, 'PRODUCTS_PROVED'))),
                'ALVOS_CITADOS': dict(Counter(
                    t for a in comp for t in _lista(a, 'ISSUE_TERMS'))),
                'POR_MES': dict(Counter((a.get('START_DATE') or 'SEM_DATA')[:7]
                                        for a in comp)),
                'REGIOES': dict(Counter(r for a in comp for r in _lista(a, 'REGION_IDS'))),
                'LIMITE': ('AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY. Alcance nao e '
                           'mira, e comunicacao nao e participacao de mercado. Sem '
                           'serie por ano nao ha baseline: nao se diz "aumento".'),
            },
            'SINAIS_DE_CAMPO': {
                'TOTAL': len(sinais),
                'POR_REGIAO': dict(Counter(g for r in sinais for g in _lista(r, 'REGION_IDS'))),
                'POR_ALVO': dict(Counter(i for r in sinais for i in _lista(r, 'ISSUE_IDS'))),
                'POR_MES': dict(Counter(str(r.get('REFERENCE_DATE'))[:7] for r in sinais)),
            },
            'JANELAS': {
                'TOTAL_PARA_ESTA_CULTURA': len(janelas),
                'TOTAL_NO_PACOTE_INTEIRO': len(pkg['currentFieldSignals']),
                'CULTURAS_COM_JANELA': sorted({w.get('CROP') for w in
                                               pkg['currentFieldSignals']}),
                'LEI': ('sem registro de janela para a cultura, ABERTA / POR_ABRIR / '
                        'FECHADA sao todas NAO SEI. Nao se deriva janela de calendario.'),
            },
        }

    testemunhas = {
        'VITE_DA_VINO': testemunha('CROP_GRAPEVINE', [
            'ISSUE_DOWNY_MILDEW', 'ISSUE_POWDERY_MILDEW', 'ISSUE_BOTRYTIS',
            'ISSUE_GRAPE_MOTH', 'ISSUE_SCAPHOIDEUS', 'ISSUE_APHIDS']),
        'MAIS': testemunha('CROP_MAIZE', [
            'ISSUE_CORN_BORER', 'ISSUE_DIABROTICA', 'ISSUE_APHIDS',
            'ISSUE_WEEDS_GENERIC', 'ISSUE_AMARANTHUS', 'ISSUE_ECHINOCHLOA']),
    }

    # -- A PERDA DE CULTURA DO CATALOGO, MEDIDA UMA VEZ SO -------------------
    # O censo do catalogo guarda o que a FICHA DE CADA PRODUTO declara. O
    # pacote guarda outra coisa: em que PAGINA DE CULTURA o produto apareceu -
    # e so sete paginas de cultura foram lidas. Sao duas perguntas diferentes,
    # e a segunda foi tomada pela primeira.
    #
    #     <<NAO O ENCONTREI NA PAGINA QUE LI>> NAO E <<ELE NAO ESTA LA>>.
    pares_censo = sum(len(p.get('CROPS_DECLARED_ON_PAGE') or []) for p in censo)
    pares_pacote = sum(len(p.get('CROPS_DECLARED_ON_SITE') or [])
                       for p in pkg['productsCommercial'])
    culturas_censo = {c for p in censo for c in (p.get('CROPS_DECLARED_ON_PAGE') or [])}
    culturas_pacote = {c for p in pkg['productsCommercial']
                       for c in (p.get('CROPS_DECLARED_ON_SITE') or [])}
    perda_catalogo = {
        'PARES_PRODUTO_x_CULTURA_NO_CENSO': pares_censo,
        'PARES_PRODUTO_x_CULTURA_NO_PACOTE': pares_pacote,
        'PARES_PERDIDOS': pares_censo - pares_pacote,
        'CULTURAS_DISTINTAS_NO_CENSO': len(culturas_censo),
        'CULTURAS_DISTINTAS_NO_PACOTE': len(culturas_pacote),
        'CAUSA': ('CROPS_DECLARED_ON_SITE nao vem da ficha do produto: vem de '
                  'CULTURA_PAGINA em scripts/adama_catalogo_montar.py, que so '
                  'conhece as paginas de cultura lidas. O proprio ficheiro ja '
                  'declara o limite em CULTURA_LEIA_ASSIM - o que faltava era '
                  'o consumidor a jusante respeitar essa declaracao.'),
        'ONDE_DOI': ('PORTFOLIO_MATCHES cruza o produto com o catalogo. Ausencia '
                     'no catalogo vira exclusao no ecra, e a ausencia e do '
                     'nosso rastreio, nao do catalogo.'),
    }

    os.makedirs(SAIDA, exist_ok=True)
    rel = {
        'MEDIDA': 'COMPLETUDE-DA-OPORTUNIDADE',
        'PACOTE_MEDIDO': pkg.get('buildId'),
        'DATA_DE_REFERENCIA': pkg.get('referenceDate'),
        'PERDA_DE_CULTURA_DO_CATALOGO': perda_catalogo,
        'CASOS_TESTEMUNHA': testemunhas,
        'TOTAIS': {
            'OPORTUNIDADES': len(fichas),
            'CARTOES_CORTADOS_PELO_TETO_12': sum(
                1 for f in fichas if (f['FUNIL']['PERDIDO_PELO_CORTE_12'] or 0) > 0),
            'PRODUTOS_REMOVIDOS_PELO_TETO_12': sum(
                (f['FUNIL']['PERDIDO_PELO_CORTE_12'] or 0) for f in fichas),
            'CARTOES_SEM_ENTRADA_RECONSTRUIDA': sum(
                1 for f in fichas if f['FUNIL']['PERDIDO_PELO_CORTE_12'] is None),
            'PRODUTOS_PERDIDOS_AO_CASAR_COM_CATALOGO': sum(
                f['FUNIL']['PERDIDO_AO_CASAR_COM_CATALOGO'] for f in fichas),
            'PRODUTOS_PERDIDOS_PELO_PORTAO_CLIENT_SAFE': sum(
                f['FUNIL']['PERDIDO_PELO_PORTAO_CLIENT_SAFE'] for f in fichas),
            'CARTOES_EM_QUE_AS_DUAS_TELAS_DIVERGEM': sum(
                1 for f in fichas if f['FUNIL']['AS_DUAS_TELAS_DIVERGEM']),
            'COM_VARREDURA_DE_PORTFOLIO_INCOMPLETA': sum(
                1 for f in fichas
                if f['PORTFOLIO']['PRODUTOS_ADAMA_ENCONTRADOS'] >
                f['FUNIL']['5_APOS_CORTE_12']),
            'CONTA_DO_PORTFOLIO_FECHA_EM_TODAS': all(
                f['PORTFOLIO']['CONTA_FECHA'] for f in fichas),
            'COM_PRODUTO_MOSTRADO_SEM_LASTRO': sum(
                1 for f in fichas if f['PORTFOLIO']['MOSTRADOS_SEM_LASTRO']),
            'CRUZAMENTOS_ENCONTRADOS': sum(f['FAMILIAS_COM_MATCH'] for f in fichas),
            'COM_MATCH_DE_VIDEO': sum(
                1 for f in fichas if f['CRUZAMENTO']['VIDEOS']['MATCH_FORTE'] > 0),
            'COM_MATCH_DE_CIENCIA': sum(
                1 for f in fichas if f['CRUZAMENTO']['CIENCIA']['RESULTADO'] == 'MATCH'),
            'COM_MATCH_DE_PESQUISADOR': sum(
                1 for f in fichas
                if f['CRUZAMENTO']['PESQUISADORES']['MATCH_SO_CULTURA'] > 0),
            'COM_MATCH_DE_CONCORRENTE': sum(
                1 for f in fichas
                if f['CRUZAMENTO']['CONCORRENCIA']['MATCH_SO_CULTURA'] > 0),
            'COM_CONVERGENCIA_MULTIFAMILIA': sum(
                1 for f in fichas if f['FAMILIAS_COM_MATCH'] >= 3),
        },
        'MAIS_CONECTADAS': [
            {'ID': f['ID'], 'CULTURA': f['CULTURA'], 'ALVO': f['ALVO'],
             'FAMILIAS_COM_MATCH': f['FAMILIAS_COM_MATCH']}
            for f in sorted(fichas, key=lambda x: -x['FAMILIAS_COM_MATCH'])[:10]],
        'LEI': ('esta medida NAO promove nem rebaixa oportunidade nenhuma. Conta o '
                'que estava disponivel para olhar e o que foi olhado. A classe C '
                '(NAO SEI) e resultado valido e obrigatorio.'),
        'OPORTUNIDADES': len(fichas),
        'FAMILIAS_NO_PACOTE': sorted(FAMILIAS),
        'FAMILIAS_FORA_DO_PACOTE': sorted(FAMILIAS_FORA_DO_PACOTE),
        'MOTOR_CARREGA': sorted(carregadas),
        'MOTOR_USA': sorted(usadas),
        'MOTOR_CARREGA_E_NAO_USA': sorted(carregadas - usadas),
        'FICHAS': fichas,
    }
    p = os.path.join(SAIDA, 'IT-COMPLETUDE-OPORTUNIDADE.json')
    json.dump(rel, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('escrito %s' % os.path.relpath(p, ROOT))
    return rel


# Ponte entre o nome da colecao no pacote servido e o nome do ficheiro que o
# motor carrega. Sem ela, MOTOR_CONSULTA seria adivinhacao.
_COL2ING = {
    'productRelationships': 'PRODUCT-RELATIONSHIPS',
    'productsCommercial': 'PRODUCTS-COMMERCIAL',
    'productsRegulatory': 'PRODUCTS-REGULATORY',
    'activeIngredients': 'ACTIVE-INGREDIENTS',
    'productActiveIngredients': 'PRODUCT-ACTIVE-INGREDIENTS',
    'fieldBulletins': 'CURRENT-FIELD-SIGNALS',
    'currentFieldSignals': 'CROP-WINDOWS',
    'agrometConditions': 'AGROMET-CONDITIONS',
    'scienceRecords': 'SCIENCE',
    'researchers': 'RESEARCHERS',
    'publicVoices': 'PUBLIC-VOICES',
    'publicChannels': 'PUBLIC-CHANNELS',
    'competitorActivities': 'COMPETITOR-ACTIVITIES',
    'regulatoryFutureFacts': 'REGULATORY-FUTURE-FACTS',
    'regulatoryFuture': 'REGULATORY-FUTURE',
    'events': 'EVENTS',
    'futureEvents': 'FUTURE-EVENTS',
    'marketObservations': 'MARKET-OBSERVATIONS',
    'cropEconomics': 'CROP-ECONOMIC-WEIGHT',
    'resistance': 'RESISTANCE',
    'news': 'NEWS',
    'futureSignals': 'FUTURE-SIGNALS',
    'relationships': 'RELATIONSHIPS',
    'clientSafeCrossings': 'CLIENT-SAFE-CROSSINGS',
}


if __name__ == '__main__':
    main()
