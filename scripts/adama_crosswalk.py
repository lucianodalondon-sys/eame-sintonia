#!/usr/bin/env python3
"""
CROSSWALK ADAMA ↔ MAPA — a contraprova regulatória do censo (seções 16, 17 e 23).

Duas metades, e elas falham de formas diferentes:

    metade REGULATÓRIA   MAPA/ROPF. Viva neste ambiente. 188 registros ADAMA, 96 vigentes.
    metade COMERCIAL     catálogo público da ADAMA. Negada na borda (ver adama_es_portao).

O crosswalk EXISTE mesmo com uma metade ausente — só não pode ser CONCLUÍDO. A diferença
importa: sem catálogo observado, um registro do ROPF não é ROPF_ONLY. ROPF_ONLY afirma
"está no MAPA e NÃO está no catálogo", e isso exige ter LIDO o catálogo. Sem leitura o
estado é NOT_TESTABLE_WITHOUT_CATALOG, que é ignorância medida, não achado.

    python3 scripts/adama_crosswalk.py --vocabulario      # baixa idCultivo/idPlaga (vivo)
    python3 scripts/adama_crosswalk.py --par TRIGO "SEPTORIOSIS DEL TRIGO, ZYMOSEPTORIA TRITICI"
    python3 scripts/adama_crosswalk.py --crosswalk        # estado atual das duas metades
"""
import html as _html
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, HERE)
import mapa_regfi as M          # noqa: E402

VOCAB_ID = os.path.join(SAMPLES, 'ES-MAPA-VOCABULARIO-IDS.json')
ROPF = os.path.join(SAMPLES, 'ES-ADAMA-PORTFOLIO-ROPF.json')


def _chave(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', s).strip()


# ══════════════════════════════════════════════════════════════════════════════
# 1 · O VOCABULÁRIO COM ID — o que faltava para a rota do par ser executável
# ══════════════════════════════════════════════════════════════════════════════
#
# ES-ROTA-DO-PAR-CROP-ISSUE provou que o ROPF cruza idCultivo × idPlaga no servidor.
# O que aquela rota não trazia era a TABELA de ids. Ela está publicada em texto aberto
# nos <option> de /regfiweb/Productos/Index — os mesmos que qualquer visitante recebe.
# 448 cultivos e 708 pragas: exatamente o vocabulário que o ES-ADAMA-PORTFOLIO-ROPF
# já dizia usar, agora com a chave que torna o par perguntável.

COMBOS = {'crops': 'cmbCultivosSearch', 'issues': 'cmbPlagaSearch'}


def baixar_vocabulario_com_ids():
    html = M._get('Productos/Index').decode('utf-8', 'replace')
    fora = {}
    for eixo, sid in COMBOS.items():
        i = html.find('id="%s"' % sid)
        if i < 0:
            fora[eixo] = {}
            continue
        j = html.find('</select>', i)
        seg = html[i:j] if j > 0 else html[i:]
        opts = re.findall(r'<option value="(\d+)"[^>]*>([^<]+)', seg)
        # o MAPA serve os rótulos com entidade HTML ("MA&#xCD;Z"). Sem unescape, MAÍZ e
        # as três variantes de milho ficam inalcançáveis — e a seção 22 depende delas.
        fora[eixo] = {}
        for vid, nome in opts:
            nome = _html.unescape(nome).strip()
            if nome:
                fora[eixo][_chave(nome)] = {'ID': int(vid), 'LABEL': nome}
    return fora


def vocabulario_com_ids(baixar_se_faltar=True):
    if os.path.exists(VOCAB_ID):
        with open(VOCAB_ID, encoding='utf-8') as f:
            d = json.load(f)
        return {'crops': d['CROPS'], 'issues': d['ISSUES'], 'ORIGEM': 'CACHE_DO_REPO',
                'captured_at': d.get('captured_at')}
    if not baixar_se_faltar:
        return {'crops': {}, 'issues': {}, 'ORIGEM': 'AUSENTE'}
    v = baixar_vocabulario_com_ids()
    return {'crops': v['crops'], 'issues': v['issues'], 'ORIGEM': 'MAPA_AO_VIVO'}


def snapshot_vocabulario(captura):
    v = baixar_vocabulario_com_ids()
    return {
        'SOURCE_ID': 'ES-MAPA-VOCABULARIO-IDS',
        'source': 'MAPA ROPF — <option> de /regfiweb/Productos/Index (cmbCultivosSearch, cmbPlagaSearch)',
        'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN', 'ORIGINAL_LANGUAGE': 'ES',
        'captured_at': captura, 'ESTADO_DO_REGISTRO': 'CURRENT',
        'REQUEST': 'GET /regfiweb/Productos/Index',
        'PARA_QUE_SERVE': ('a chave idCultivo/idPlaga que torna executavel a rota do par '
                           'descrita em ES-ROTA-DO-PAR-CROP-ISSUE'),
        'CROP_COUNT': len(v['crops']), 'ISSUE_COUNT': len(v['issues']),
        'CROPS': v['crops'], 'ISSUES': v['issues'],
        'O_QUE_ISTO_NAO_E': ('nao e lista de produtos, nao e autorizacao e nao e mercado. '
                             'E o vocabulario controlado do registro espanhol.'),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2 · A ROTA DO PAR — seção 17, perguntada ao MAPA em vez de extraída de PDF
# ══════════════════════════════════════════════════════════════════════════════

def resolver(termo, tabela):
    """(ID, LABEL, ESTADO). Sem exato e sem candidato único -> AMBIGUOUS, nunca palpite."""
    k = _chave(termo)
    if k in tabela:
        return tabela[k]['ID'], tabela[k]['LABEL'], 'EXACT'
    # o MAPA rotula "NOME COMUM, NOME CIENTÍFICO"; casar por um dos lados é ler a notação
    cand = [v for kk, v in tabela.items()
            if kk == k or any(_chave(p) == k for p in v['LABEL'].split(','))]
    if len(cand) == 1:
        return cand[0]['ID'], cand[0]['LABEL'], 'MATCHED_WITH_EVIDENCE'
    if len(cand) > 1:
        return None, [c['LABEL'] for c in cand[:8]], 'AMBIGUOUS'
    # forma curta que encabeça vários rótulos oficiais — o caso "MILDIU", "VID"
    cabeca = [v for kk, v in tabela.items() if kk.split(' ')[0] == k]
    if len(cabeca) == 1:
        return cabeca[0]['ID'], cabeca[0]['LABEL'], 'MATCHED_WITH_EVIDENCE'
    if len(cabeca) > 1:
        return None, [c['LABEL'] for c in cabeca[:8]], 'AMBIGUOUS'
    return None, None, 'NOT_IN_MAPA_VOCABULARY'


def confirmar_par(cultivo, plaga, titular='ADAMA', vocab=None):
    """A ADAMA tem registro para CULTIVO × PRAGA? A interseção é feita NO SERVIDOR.

    Devolve o estado da seção 17. `MAPA_NOT_CONFIRMED` significa: perguntado ao MAPA e
    nenhum registro ADAMA voltou. É diferente de não ter perguntado.
    """
    vocab = vocab or vocabulario_com_ids()
    id_c, rot_c, est_c = resolver(cultivo, vocab['crops'])
    id_p, rot_p, est_p = resolver(plaga, vocab['issues'])

    if est_c in ('AMBIGUOUS', 'NOT_IN_MAPA_VOCABULARY') or \
       est_p in ('AMBIGUOUS', 'NOT_IN_MAPA_VOCABULARY'):
        return {'CROP': cultivo, 'ISSUE': plaga,
                'CROP_RESOLUTION': est_c, 'ISSUE_RESOLUTION': est_p,
                'CROP_CANDIDATES': rot_c if est_c == 'AMBIGUOUS' else None,
                'ISSUE_CANDIDATES': rot_p if est_p == 'AMBIGUOUS' else None,
                'ESTADO': 'AMBIGUOUS',
                'PORQUE': 'o termo nao resolve a UM id oficial; perguntar seria perguntar outra coisa'}

    total_geral, _ = M.grid(IdCultivo=id_c, IdPlaga=id_p)
    total_adama, linhas = M.grid(IdCultivo=id_c, IdPlaga=id_p, Titular=titular)
    return {
        'CROP': cultivo, 'CROP_MAPA_LABEL': rot_c, 'CROP_ID': id_c,
        'ISSUE': plaga, 'ISSUE_MAPA_LABEL': rot_p, 'ISSUE_ID': id_p,
        'CROP_RESOLUTION': est_c, 'ISSUE_RESOLUTION': est_p,
        'REGISTROS_TOTAL': total_geral,
        'REGISTROS_ADAMA': total_adama,
        'AMOSTRA_ADAMA': [n for n, _ in linhas][:5],
        'ESTADO': 'MAPA_CONFIRMED' if total_adama else 'MAPA_NOT_CONFIRMED',
        'REQUEST': 'GET /regfiweb/Productos/ProductosGrid?IdCultivo=%s&IdPlaga=%s&Titular=%s'
                   % (id_c, id_p, titular),
        'EVIDENCE_LEVEL': 'REGULATORY_FACT',
        'O_QUE_ISTO_NAO_E': ('registro autorizado nao e produto comercializado, nao e '
                             'recomendacao agronomica e nao e disponibilidade (secao 24)'),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 3 · CROSSWALK — seção 16, e a honestidade da seção 23
# ══════════════════════════════════════════════════════════════════════════════

def fichas_ropf():
    if not os.path.exists(ROPF):
        return []
    with open(ROPF, encoding='utf-8') as f:
        return json.load(f).get('FICHAS') or []


def cruzar(produtos_site, fichas):
    """Os cinco estados da seção 16, em ordem de força da evidência.

    A ordem é lei: registro exato primeiro, composição+titular depois, nome comercial
    só como APOIO. Nome comercial sozinho nunca fecha um match — é o fuzzy silencioso
    que a seção 16 proíbe.
    """
    por_reg = {_chave(f['REG']): f for f in fichas}
    por_nome = {}
    for f in fichas:
        por_nome.setdefault(_chave(f['NOME']), []).append(f)

    linhas, casadas = [], set()

    for p in produtos_site:
        reg = _chave(p.get('REGISTRATION_ID') or '')
        nome = _chave(p.get('DISPLAY_NAME') or '')

        if reg and reg in por_reg:
            f = por_reg[reg]
            casadas.add(f['REG'])
            linhas.append(_linha(p, f, 'MATCHED_EXACT', 'registration_id identico'))
            continue

        cand = por_nome.get(nome) or []
        if len(cand) == 1:
            f = cand[0]
            # nome comercial sozinho é APOIO, não prova. Só fecha com composição.
            forte = _composicao_bate(p, f)
            casadas.add(f['REG'])
            linhas.append(_linha(
                p, f,
                'MATCHED_WITH_EVIDENCE' if forte else 'AMBIGUOUS',
                'nome comercial identico + composicao compativel' if forte else
                'nome comercial identico, composicao NAO confirmada — nome sozinho nao fecha'))
            continue
        if len(cand) > 1:
            linhas.append(_linha(p, None, 'AMBIGUOUS',
                                 'nome casa %d registros distintos' % len(cand)))
            continue

        linhas.append(_linha(p, None, 'ADAMA_SITE_ONLY',
                             'sem registro nem nome correspondente no ROPF vigente'))

    for f in fichas:
        if f['REG'] not in casadas:
            linhas.append({
                'PRODUCT_ID': None, 'DISPLAY_NAME': f['NOME'], 'REG': f['REG'],
                'FORMULADO': f.get('FORMULADO'),
                'ESTADO': 'ROPF_ONLY' if produtos_site else 'NOT_TESTABLE_WITHOUT_CATALOG',
                'EVIDENCIA': ('vigente no ROPF e ausente do catalogo lido'
                              if produtos_site else
                              'o catalogo da ADAMA nao foi lido nesta rodada — sem leitura, '
                              'ausencia no catalogo NAO e afirmavel'),
            })

    return linhas


def _linha(p, f, estado, evidencia):
    return {
        'PRODUCT_ID': p.get('PRODUCT_ID'), 'DISPLAY_NAME': p.get('DISPLAY_NAME'),
        'PAGE_URL': p.get('PAGE_URL'),
        'REG': (f or {}).get('REG'), 'FORMULADO': (f or {}).get('FORMULADO'),
        'ESTADO': estado, 'EVIDENCIA': evidencia,
    }


def _composicao_bate(p, f):
    formulado = _chave(f.get('FORMULADO') or '')
    for ia in (p.get('ACTIVE_INGREDIENTS') or []):
        n = _chave(ia.get('NAME') or '')
        if len(n) >= 5 and n in formulado:
            return True
    return False


def resumo(linhas, fichas):
    conta = {}
    for l in linhas:
        conta[l['ESTADO']] = conta.get(l['ESTADO'], 0) + 1
    houve_catalogo = any(l.get('PRODUCT_ID') for l in linhas)
    return {
        'ROPF_ACTIVE_REGISTRATIONS': len(fichas),
        'PUBLIC_CATALOG_ENTRIES': (sum(1 for l in linhas if l.get('PRODUCT_ID'))
                                   if houve_catalogo else 'NOT_COLLECTED'),
        'MATCHED_EXACT': conta.get('MATCHED_EXACT', 0),
        'MATCHED_WITH_EVIDENCE': conta.get('MATCHED_WITH_EVIDENCE', 0),
        'AMBIGUOUS': conta.get('AMBIGUOUS', 0),
        'ADAMA_SITE_ONLY': conta.get('ADAMA_SITE_ONLY', 0),
        'ROPF_ONLY': conta.get('ROPF_ONLY', 'NOT_TESTABLE_WITHOUT_CATALOG'),
        'NOT_TESTABLE_WITHOUT_CATALOG': conta.get('NOT_TESTABLE_WITHOUT_CATALOG', 0),
        'PORQUE_NAO_SE_SUBTRAI': (
            'registro nao e produto e catalogo nao e registro — 96 e 55 contam unidades '
            'diferentes. Um produto pode ter varios registros; um registro pode nao ter '
            'exposicao comercial. A diferenca so vira achado DEPOIS do crosswalk, nunca '
            'por subtracao (secao 23).'),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4 · MILHO — seção 22, a metade que ESTE ambiente consegue medir
# ══════════════════════════════════════════════════════════════════════════════
#
# A seção 22 pede o mapa PÚBLICO do portfólio de milho: o que a ADAMA comunica. Esse
# lado depende do site, que está negado na borda. O que sobra é o lado REGULATÓRIO, e
# ele não é substituto: dizer "a ADAMA posiciona X em milho" é afirmação de marketing;
# "a ADAMA tem registro para X em milho contra Y" é fato regulatório. Este bloco produz
# só o segundo, e o rotula como tal.
#
# O varrido é LIMITADO por evidência: só os agentes que as fichas ADAMA já declaram.
# Varrer 708 pragas × 4 milhos seriam 2.832 perguntas ao MAPA para achar as poucas que
# existem — descortesia com a fonte, e nenhuma informação a mais.

MILHOS = ('maiz', 'maiz de grano', 'maiz dulce', 'maiz forrajero')


def mapa_regulatorio_do_milho(captura, vocab=None):
    vocab = vocab or vocabulario_com_ids()
    fichas = fichas_ropf()
    por_nome = {_chave(f['NOME']): f for f in fichas}

    variantes, produtos_milho = [], {}
    for chave in MILHOS:
        if chave not in vocab['crops']:
            continue
        c = vocab['crops'][chave]
        linhas, _ = M.export(idCultivo=c['ID'], titular='ADAMA')
        nomes = sorted({r['Nombre'] for r in linhas})
        variantes.append({'CROP_VARIANT': c['LABEL'], 'CROP_ID': c['ID'],
                          'ADAMA_REGISTRATIONS': len(linhas), 'PRODUCTS': nomes})
        for r in linhas:
            produtos_milho.setdefault(r['Nombre'], {
                'NOME': r['Nombre'], 'REG': r['NumRegistro'],
                'FORMULADO': r['Formulado'], 'ESTADO': r['Estado'],
                'TITULAR': r['Titular'], 'CADUCIDAD': r.get('StrFechaCaducidad'),
                'CROP_VARIANTS': []})
            produtos_milho[r['Nombre']]['CROP_VARIANTS'].append(c['LABEL'])

    candidatos = set()
    for nome in produtos_milho:
        f = por_nome.get(_chave(nome))
        for a in (f or {}).get('AGENTES') or []:
            candidatos.add(a)

    pares, nao_confirmados, ambiguos = [], [], []
    for chave in MILHOS:
        if chave not in vocab['crops']:
            continue
        c = vocab['crops'][chave]
        for agente in sorted(candidatos):
            r = confirmar_par(c['LABEL'], agente, vocab=vocab)
            if r['ESTADO'] == 'MAPA_CONFIRMED':
                pares.append({'CROP': c['LABEL'], 'CROP_ID': c['ID'],
                              'ISSUE': r['ISSUE_MAPA_LABEL'], 'ISSUE_ID': r['ISSUE_ID'],
                              'ADAMA_REGISTRATIONS': r['REGISTROS_ADAMA'],
                              'ALL_REGISTRATIONS': r['REGISTROS_TOTAL'],
                              'ADAMA_SAMPLE': r['AMOSTRA_ADAMA'],
                              'EVIDENCE_LEVEL': 'REGULATORY_FACT'})
            elif r['ESTADO'] == 'AMBIGUOUS':
                ambiguos.append({'CROP': c['LABEL'], 'ISSUE': agente,
                                 'PORQUE': r['PORQUE']})
            else:
                nao_confirmados.append({'CROP': c['LABEL'], 'ISSUE': agente})

    substancias = sorted({p['FORMULADO'] for p in produtos_milho.values() if p['FORMULADO']})
    return {
        'SOURCE_ID': 'ADAMA-ES-MAIZE-REGULATORY-MAP',
        'source': 'MAPA ROPF — export por idCultivo e grade por idCultivo x idPlaga',
        'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN', 'ORIGINAL_LANGUAGE': 'ES',
        'captured_at': captura, 'ESTADO_DO_REGISTRO': 'CURRENT',
        'EVIDENCE_LEVEL': 'REGULATORY_FACT',
        'CROP_VARIANTS': variantes,
        'MAIZE_PRODUCTS': sorted(produtos_milho.values(), key=lambda p: p['NOME']),
        'MAIZE_PRODUCT_COUNT': len(produtos_milho),
        'ISSUE_CANDIDATES_TESTED': sorted(candidatos),
        'MAIZE_CROP_ISSUE_RELATIONS': pares,
        'PAIRS_TESTED_NOT_CONFIRMED': len(nao_confirmados),
        'PAIRS_AMBIGUOUS': ambiguos,
        'MAIZE_FORMULATIONS': substancias,
        'O_QUE_ISTO_E': ('o mapa REGULATORIO do milho: onde a ADAMA tem registro vigente. '
                         'Cada par foi PERGUNTADO ao MAPA, nao derivado de lista.'),
        'O_QUE_ISTO_NAO_E': (
            'NAO e o mapa PUBLICO pedido pela secao 22. Posicionamento, tecnologia propria, '
            'claim, dose comunicada e janela declarada vivem no site da ADAMA, que esta '
            'negado na borda para este ambiente (ver PORTAO-ADAMA-ES). Registro nao e '
            'comunicacao, e nenhum dos dois e venda.'),
        'MAIZE_PUBLIC_POSITIONING': 'NOT_COLLECTED — depende do site da ADAMA',
        'MAIZE_TECHNOLOGIES': 'NOT_COLLECTED — depende do site da ADAMA',
    }


if __name__ == '__main__':
    if '--vocabulario' in sys.argv:
        i = sys.argv.index('--vocabulario')
        cap = sys.argv[i + 1] if len(sys.argv) > i + 1 else 'NÃO SEI'
        print(json.dumps(snapshot_vocabulario(cap), ensure_ascii=False, indent=1))
        sys.exit(0)
    if '--par' in sys.argv:
        i = sys.argv.index('--par')
        print(json.dumps(confirmar_par(sys.argv[i + 1], sys.argv[i + 2]),
                         ensure_ascii=False, indent=1))
        sys.exit(0)
    if '--milho' in sys.argv:
        i = sys.argv.index('--milho')
        cap = sys.argv[i + 1] if len(sys.argv) > i + 1 else 'NÃO SEI'
        print(json.dumps(mapa_regulatorio_do_milho(cap), ensure_ascii=False, indent=1))
        sys.exit(0)
    if '--crosswalk' in sys.argv:
        f = fichas_ropf()
        linhas = cruzar([], f)
        print(json.dumps(resumo(linhas, f), ensure_ascii=False, indent=1))
        sys.exit(0)
    print(__doc__)
