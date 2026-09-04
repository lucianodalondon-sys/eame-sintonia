#!/usr/bin/env python3
"""FASE 4 — propaga o conjunto de pares novo SOMENTE ate a camada de portfolio.

O que este arquivo faz e o que ele recusa fazer
-----------------------------------------------
O conjunto de pares mudou de 2.030 para 2.313. Isso muda QUAIS ROTULOS alcancam
cada oportunidade, e portanto quais PRODUTOS do catalogo aparecem nela. So isso.

    NAO recalcula SIGNAL, DIRECTION, THRESHOLD, WINDOW, STAGE, GEOGRAPHY nem
    WHY_NOW agronomico. Nenhum deles depende do rotulo: eles nascem do sinal de
    campo e da fonte que o declara. Recalcula-los porque o rotulo mudou seria
    deixar o portfolio decidir a agronomia — o avesso da ordem correta.

A regra do PRIMARY_MATCH e a do MOTOR, copiada e nao reinventada
----------------------------------------------------------------
    1. a fonte nomeia a substancia e so um produto a tem  -> FONTE_NOMEIA_A_SUBSTANCIA
    2. ha exatamente um produto no par                    -> UNICO_PRODUTO_DO_CATALOGO_NO_PAR
    3. qualquer outro caso                                -> None, SEM_REGRA_DEFENSAVEL

Nunca portfolio[0]. Ordenar a lista por nome e apresentacao, nao eleicao.

Rodagem: precisa da worktree destacada da branch canonica (b3935bd), porque o
vocabulario e o pacote das 43 moram la. Nada e escrito naquela arvore.
"""
import argparse
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(AQUI)


def carregar(wt):
    sys.path.insert(0, os.path.join(wt, 'scripts'))
    import v21_normalizar as N            # noqa: E402
    P = os.path.join(wt, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

    def j(nome):
        d = json.load(open(os.path.join(P, nome), encoding='utf-8'))
        return d['RECORDS'] if isinstance(d, dict) and 'RECORDS' in d else d

    return N, {
        'OPP': j('OPPORTUNITIES.json'),
        'REL_OLD': j('PRODUCT-RELATIONSHIPS.json'),
        'COM': j('PRODUCTS-COMMERCIAL.json'),
        'AI': j('PRODUCT-ACTIVE-INGREDIENTS.json'),
        'ING': j('ACTIVE-INGREDIENTS.json'),
    }


def num(x):
    s = ''.join(c for c in str(x or '') if c.isdigit())
    return s.zfill(6) if s else ''


def pares_novos(N):
    """O conjunto publicado, traduzido para o namespace do motor com o
    vocabulario DO MOTOR. Par cujo alvo nao tem ISSUE_ID canonico entra com
    ISSUE_ID None — e fica visivel como lacuna, em vez de ser descartado calado."""
    d = json.load(open(os.path.join(
        ROOT, 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json'),
        encoding='utf-8'))
    fora = []
    for p in d['PAIRS']:
        fora.append({
            'REGISTRATION_NUMBER': num(p['REGISTRATION_ID']),
            'PRODUCT_NAME': p.get('PRODUCT'),
            'CROP_ON_LABEL': p['CROP'],
            'TARGET_ON_LABEL': p['TARGET'],
            'CROP_ID': N.crop_id(p['CROP']),
            'ISSUE_ID': N.issue_id(p['TARGET']),
            'TARGET_AS_WRITTEN': p.get('TARGET_AS_WRITTEN'),
            'ROUTE': p.get('ROUTE'),
        })
    return fora


def chave(r):
    # '' no lugar de None: a chave precisa ordenar, e par sem id canonico ainda
    # e um par — descarta-lo por causa da ordenacao seria perder a lacuna.
    return (r.get('CROP_ID') or '', r.get('ISSUE_ID') or '',
            num(r.get('REGISTRATION_NUMBER')))


def main(wt, saida):
    N, D = carregar(wt)
    velho = [{'CROP_ID': (r.get('CROP_IDS') or [None])[0],
              'ISSUE_ID': (r.get('ISSUE_IDS') or [None])[0],
              'REGISTRATION_NUMBER': num(r.get('REGISTRATION_NUMBER')),
              'PRODUCT_NAME': r.get('PRODUCT_NAME'),
              'CROP_ON_LABEL': r.get('CROP_ON_LABEL'),
              'TARGET_ON_LABEL': r.get('TARGET_ON_LABEL')} for r in D['REL_OLD']]
    novo = pares_novos(N)

    kv, kn = {chave(r) for r in velho}, {chave(r) for r in novo}
    add, rem, keep = sorted(kn - kv), sorted(kv - kn), sorted(kn & kv)

    # ── indice de catalogo: registro -> produtos comerciais ─────────────────
    ix_com = collections.defaultdict(list)
    for p in D['COM']:
        r = num(p.get('MATCHED_REGULATORY_ID'))
        if r:
            ix_com[r].append(p)
    ai_por_prod = collections.defaultdict(list)
    for a in D['AI']:
        ai_por_prod[num(a.get('REGISTRATION_NUMBER'))].append(a)
    ing = {a['ID']: a for a in D['ING']}

    def alcanca(pares, crop_id, issue_id):
        """Rotulos que alcancam a oportunidade — mesma regra do motor:
        cultura tem de bater; o alvo so filtra quando a oportunidade TEM alvo."""
        return [r for r in pares
                if r.get('CROP_ID') == crop_id
                and (issue_id is None or r.get('ISSUE_ID') == issue_id)]

    # ⚠️ A UNIAO, E NAO A SUBSTITUICAO. Medido: 142 pares que o conjunto antigo
    # tinha e o novo nao tem, concentrados nos rotulos-matriz (008259, 013560,
    # 013590, 015275, 017687, 018067, 019095) — a mesma familia que o gabarito
    # EXCLUIU por nao conseguir defender a exaustividade. Ali o novo conjunto nao
    # diz "nao autorizado": ele diz "nao li". A lei desta casa e antiga e vale
    # aqui inteira:
    #
    #     AUSENCIA NA NOSSA LEITURA NUNCA E AUSENCIA NO REGISTRO.
    #
    # Deixar o conjunto novo REMOVER produto de oportunidade seria transformar
    # buraco de recall em decisao comercial. OPP_169BD86DB324 (tignoletta x
    # videira x Umbria) e OPP_3C8C3960CC66 (VALIDATE_NOW) perderiam o seu unico
    # produto por causa de uma tabela que o parser le pela metade.
    def uniao(pa_v, pa_n):
        return pa_v + [r for r in pa_n if chave(r) not in {chave(x) for x in pa_v}]

    def produtos(pares_alc):
        vistos, fora = set(), []
        for r in pares_alc:
            for p in ix_com.get(num(r['REGISTRATION_NUMBER']), []):
                if p['ID'] not in vistos:
                    vistos.add(p['ID'])
                    fora.append(p)
        return sorted(fora, key=lambda p: str(p.get('NAME')))

    def primario(prods, ativos_da_fonte):
        """A REGRA DO MOTOR, copiada. Nunca a posicao do array."""
        nomeados = []
        for p in prods:
            ats = [ing.get(x.get('ACTIVE_INGREDIENT_ID'))
                   for x in ai_por_prod.get(num(p.get('MATCHED_REGULATORY_ID')), [])]
            if any(a and (a.get('NAME') or '').upper() in ativos_da_fonte
                   for a in ats):
                nomeados.append(p)
        if len(nomeados) == 1:
            return nomeados[0]['ID'], 'FONTE_NOMEIA_A_SUBSTANCIA'
        if len(prods) == 1:
            return prods[0]['ID'], 'UNICO_PRODUTO_DO_CATALOGO_NO_PAR'
        return None, 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER'

    linhas, mudou_n, prim_mudou = [], 0, 0
    for o in D['OPP']:
        crop = (o.get('CROP_IDS') or [None])[0]
        issue = (o.get('ISSUE_IDS') or [None])[0]
        ativos_fonte = set(o.get('SOURCE_NAMED_ACTIVES') or [])
        pa_v, pa_n = alcanca(velho, crop, issue), alcanca(novo, crop, issue)
        pv = produtos(pa_v)
        pn = produtos(uniao(pa_v, pa_n))        # UNIAO — ver comentario acima
        so_novo = produtos(pa_n)                # o que o conjunto novo sozinho ve
        idv = {p['ID'] for p in pv}
        idn = {p['ID'] for p in pn}
        idso = {p['ID'] for p in so_novo}
        prim_v, raz_v = primario(pv, ativos_fonte)
        prim_n, raz_n = primario(pn, ativos_fonte)
        mudou = idv != idn
        mudou_n += 1 if mudou else 0
        prim_mudou += 1 if prim_v != prim_n else 0
        linhas.append({
            'OPPORTUNITY_ID': o['ID'],
            'CROP': o.get('CROP'), 'TARGET': o.get('TARGET'),
            'GEOGRAPHY': o.get('GEOGRAPHY'), 'STATUS': o.get('STATUS'),
            'COMMERCIAL_PRIORITY': o.get('COMMERCIAL_PRIORITY'),
            'CROP_ID': crop, 'ISSUE_ID': issue,
            'LABELS_REACHING_BEFORE': len(pa_v), 'LABELS_REACHING_AFTER': len(pa_n),
            'OLD_PRODUCTS': sorted(str(p.get('NAME')) for p in pv),
            'NEW_PRODUCTS': sorted(str(p.get('NAME')) for p in pn),
            'ADDED_PRODUCTS': sorted(str(p.get('NAME')) for p in pn
                                     if p['ID'] not in idv),
            'REMOVED_PRODUCTS': sorted(str(p.get('NAME')) for p in pv
                                       if p['ID'] not in idn),
            'PRIMARY_MATCH_BEFORE': prim_v, 'PRIMARY_MATCH_REASON_BEFORE': raz_v,
            'PRIMARY_MATCH_AFTER': prim_n, 'PRIMARY_MATCH_REASON_AFTER': raz_n,
            'PORTFOLIO_CHANGED': mudou,
            'MERGE_RULE': 'UNIAO — o conjunto novo ACRESCENTA produto, nunca remove',
            'PRODUCTS_THE_NEW_SET_ALONE_WOULD_NOT_SEE': sorted(
                str(p.get('NAME')) for p in pv if p['ID'] not in idso),
            'RECALL_DEBT': sorted(str(p.get('NAME')) for p in pv
                                  if p['ID'] not in idso),
            'RECALCULATED_LAYERS': ['PORTFOLIO_MATCHES', 'PRIMARY_MATCH'],
            'NOT_RECALCULATED': ['SIGNAL', 'DIRECTION', 'THRESHOLD', 'WINDOW',
                                 'STAGE', 'GEOGRAPHY', 'WHY_NOW', 'STATUS',
                                 'COMMERCIAL_PRIORITY', 'PUBLICATION_STATE'],
        })

    def por(campo, conj, base):
        c = collections.Counter()
        ix = {chave(r): r for r in base}
        for k in conj:
            r = ix.get(k)
            if r:
                c[str(r.get(campo))] += 1
        return dict(c.most_common(25))

    out = {
        'DATASET': 'IT-PAIRSET-PROPAGACAO-V1',
        'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'efeito do conjunto IT-ROTULOS-PARES-V3 (2313 pares) sobre a '
                  'camada de PORTFOLIO das 43 oportunidades canonicas, '
                  'reconstruidas read-only da worktree em b3935bd',
        'CANONICAL_ENGINE_HEAD': 'b3935bd',
        'CANONICAL_BUILD_ID': 'V21-358954754db5ea2f',
        'OPPORTUNITIES_IN_ENGINE': len(D['OPP']),
        'OLD_PAIR_COUNT': len(velho),
        'NEW_PAIR_COUNT': len(novo),
        'ADDED_PAIRS': len(add),
        'REMOVED_PAIRS': len(rem),
        'UNCHANGED_PAIRS': len(keep),
        'CHAVE_DE_COMPARACAO': '(CROP_ID, ISSUE_ID, REGISTRATION_NUMBER) — no '
                               'namespace do motor, traduzido com o vocabulario '
                               'do proprio motor (v21_normalizar)',
        'PORQUE_NAO_COMPARO_LITERAL': (
            'o conjunto antigo conta o LITERAL do alvo (AMARANTO, ERIOSOMA) e o '
            'novo conta CLASSE canonica (INFESTANTI, AFIDI). Comparar literal '
            'contra classe contaria como "removido" todo par que so mudou de '
            'regua. A chave comum e o ISSUE_ID do motor, que os dois alcancam.'),
        'ADDED_BY_CROP': por('CROP_ON_LABEL', add, novo),
        'ADDED_BY_TARGET': por('TARGET_ON_LABEL', add, novo),
        'ADDED_BY_PRODUCT': por('PRODUCT_NAME', add, novo),
        'ADDED_BY_LABEL': por('REGISTRATION_NUMBER', add, novo),
        'REMOVED_BY_CROP': por('CROP_ON_LABEL', rem, velho),
        'REMOVED_BY_TARGET': por('TARGET_ON_LABEL', rem, velho),
        'REMOVED_BY_PRODUCT': por('PRODUCT_NAME', rem, velho),
        'PAIRS_WITHOUT_CANONICAL_ISSUE_ID': sum(1 for r in novo
                                                if r['ISSUE_ID'] is None),
        'PAIRS_WITHOUT_CANONICAL_CROP_ID': sum(1 for r in novo
                                               if r['CROP_ID'] is None),
        'LACUNA_DE_VOCABULARIO': (
            'par sem ISSUE_ID canonico NAO foi descartado: ele conta aqui. O '
            'motor conhece 24 problemas e 20 culturas; o conjunto de rotulos '
            'fala 61 alvos e 48 culturas. A diferenca e lacuna de vocabulario '
            'do motor, e nao ausencia de autorizacao.'),
        'MERGE_RULE': 'UNIAO. O conjunto novo so ACRESCENTA produto a oportunidade.',
        'POR_QUE_UNIAO': (
            '142 pares que o conjunto antigo tinha e o novo nao tem carregam '
            'ISSUE_ID canonico — sao perda REAL de leitura, e nao mudanca de '
            'regua. Estao concentrados nos rotulos-matriz de centenas de blocos '
            '(008259, 013560, 013590, 015275, 017687, 018067, 019095), que o '
            'gabarito EXCLUIU por nao conseguir defender a exaustividade. Ali o '
            'conjunto novo nao afirma "nao autorizado": ele nao leu. Substituir '
            'em vez de unir tiraria o unico produto de OPP_169BD86DB324 e de '
            'OPP_3C8C3960CC66 (VALIDATE_NOW) por causa de um buraco de recall.'),
        'RECALL_DEBT_PAIRS': 142,
        'RECALL_DEBT_LABELS': ['018067', '019095', '008259', '015275', '017687',
                               '013560', '013590', '017955', '007555', '007864',
                               '009800', '012023'],
        'OPPORTUNITIES_WITH_PORTFOLIO_CHANGED': mudou_n,
        'OPPORTUNITIES_WITH_PRIMARY_MATCH_CHANGED': prim_mudou,
        'PRIMARY_MATCH_RULE': 'copiada de scripts/v21_oportunidades.py::portfolio — '
                              'FONTE_NOMEIA_A_SUBSTANCIA, senao UNICO_PRODUTO, '
                              'senao None. Nunca a posicao do array.',
        'ROWS': linhas,
    }
    json.dump(out, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('OLD_PAIR_COUNT = %d' % out['OLD_PAIR_COUNT'])
    print('NEW_PAIR_COUNT = %d' % out['NEW_PAIR_COUNT'])
    print('ADDED  = %d   REMOVED = %d   UNCHANGED = %d' % (len(add), len(rem),
                                                           len(keep)))
    print('sem ISSUE_ID canonico = %d   sem CROP_ID canonico = %d'
          % (out['PAIRS_WITHOUT_CANONICAL_ISSUE_ID'],
             out['PAIRS_WITHOUT_CANONICAL_CROP_ID']))
    print()
    print('OPPORTUNITIES_IN_ENGINE                  = %d' % len(D['OPP']))
    print('OPPORTUNITIES_WITH_PORTFOLIO_CHANGED     = %d' % mudou_n)
    print('OPPORTUNITIES_WITH_PRIMARY_MATCH_CHANGED = %d' % prim_mudou)
    print()
    for r in linhas:
        if r['PORTFOLIO_CHANGED']:
            print('  %s %-16s %-22s %-16s  %d->%d produtos  +%s -%s' % (
                r['OPPORTUNITY_ID'], r['CROP_ID'] or '-',
                (r['ISSUE_ID'] or '-'), r['STATUS'],
                len(r['OLD_PRODUCTS']), len(r['NEW_PRODUCTS']),
                r['ADDED_PRODUCTS'][:3], r['REMOVED_PRODUCTS'][:3]))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--worktree', default='/home/user/wt-canonica')
    ap.add_argument('--out', default=os.path.join(
        ROOT, 'data/samples/IT-ROTULOS-V1/IT-PAIRSET-PROPAGACAO-V1.json'))
    a = ap.parse_args()
    main(a.worktree, a.out)
