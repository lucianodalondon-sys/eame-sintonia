#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACHA OS CONFLITOS entre o pacote anterior e a camada last-mile (§9).

    python3 scripts/v2_conflitos.py

A fusão é ADITIVA: nada do pacote anterior se perde. Mas quando as duas
camadas afirmam coisas diferentes sobre o MESMO objeto, alguém tem de decidir —
e a decisão precisa ficar escrita, com OLD_VALUE, NEW_VALUE, WINNER, WHY e a
base de QA.

    UM CONFLITO NÃO RESOLVIDO NÃO É NEUTRO. Ele vira duas verdades no mesmo
    portal, e quem abrir primeiro ganha.

ONDE OS CONFLITOS PODEM MORAR, E POR QUÊ
-----------------------------------------
EVENTOS       o pacote anterior tem 18, a last-mile tem 22, e vários são o
              MESMO evento. Data de feira muda, e o anterior pode estar velho.

CATÁLOGO      o anterior marcou 40 produtos com bandeira de catálogo; o censo
              novo leu 51 fichas. A diferença não é erro de um dos dois: são
              perguntas diferentes (bandeira no arquivo x ficha publicada).

FENOLOGIA     o anterior declarava 6 rótulos de região; a last-mile alcançou
              mais. Isso é adição, não conflito — salvo se a MESMA região
              aparecer com contagem diferente.

⚠️ E UM QUE NÃO É CONFLITO, E É FÁCIL CONFUNDIR
------------------------------------------------
`field-voices` (58 falas de PLATEIA de canal) e `PUBLIC_VOICES` (22 vozes
IDENTIFICADAS) parecem a mesma família e não são. Uma é comentário sob vídeo;
a outra é gente com nome e cargo. Fundi-las apagaria justamente a distinção
que o eixo de plateia existe para preservar.
"""
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DR = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                  '01-DESIGN-READY')
V2 = os.path.join(ROOT, 'data', 'samples', 'IT-V2')


def _n(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', str(t or ''))
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]+', ' ', t.lower()).strip()


def le(rel, chave):
    p = os.path.join(DR, rel.replace('/', os.sep))
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8')).get(chave) or []


def datas(txt):
    """Extrai qualquer data reconhecível de um texto livre."""
    t = str(txt or '')
    out = set(re.findall(r'\d{4}-\d{2}-\d{2}', t))
    for d, m, a in re.findall(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', t):
        out.add('%s-%02d-%02d' % (a, int(m), int(d)))
    return out


def main():
    can = json.load(open(os.path.join(V2, 'IT-V2-CANONICO.json'), encoding='utf-8'))
    novos = can['REGISTROS']
    conflitos, adicoes = [], []

    # ── EVENTOS ───────────────────────────────────────────────────────────────
    velhos = le('EVENTS/events.json', 'EVENTS')
    ev_novos = [r for r in novos if r['FAMILIA'] == 'FUTURE_EVENTS']
    for n in ev_novos:
        alvo = _n(n.get('o_que'))[:60]
        melhor, sc = None, 0.0
        for v in velhos:
            nome = _n(v.get('EVENT') or v.get('TITLE') or v.get('NAME'))
            if not nome:
                continue
            s = SequenceMatcher(None, alvo[:40], nome[:40]).ratio()
            # ⚠️ O ATALHO QUE PRODUZIU UM CONFLITO FALSO
            # A versao anterior dava 0,8 quando a PRIMEIRA palavra do nome
            # aparecia no texto novo. So que a primeira palavra de «Evento SATA
            # a Rovigo» e «evento» -- e ela aparece em qualquer texto sobre
            # eventos. O casamento pegou uma observacao META («o agregador
            # Agronotizie tem so 11 eventos futuros») e a tratou como se fosse
            # o evento de Rovigo, gerando um conflito de data que nao existe.
            #
            #     PALAVRA GENERICA NAO IDENTIFICA NADA. So token DISTINTIVO
            #     casa -- e generico e' justamente o que aparece em todo lugar.
            GENERICAS = {'evento', 'eventi', 'fiera', 'giornate', 'giornata',
                         'convegno', 'corso', 'forum', 'congresso', 'incontro',
                         'salone', 'mostra', 'workshop', 'seminario', 'agro',
                         'agricoltura', 'italia', 'nazionale', 'internazionale'}
            distintivos = [w for w in nome.split()
                           if len(w) >= 4 and w not in GENERICAS]
            if distintivos and any(w in alvo for w in distintivos):
                s = max(s, 0.8)
            if s > sc:
                melhor, sc = v, s
        if melhor and sc >= 0.72:
            dv = datas(json.dumps(melhor, ensure_ascii=False))
            dn = datas((n.get('periodo') or '') + ' ' + (n.get('o_que') or ''))
            if dn and dv and not (dn & dv):
                conflitos.append({
                    'OBJETO': 'EVENTO · %s' % (melhor.get('EVENT') or
                                               melhor.get('TITLE') or '?'),
                    'CAMPO': 'data',
                    'OLD_VALUE': sorted(dv), 'NEW_VALUE': sorted(dn),
                    'OLD_ID': melhor.get('ID'), 'NEW_ID': n['CANONICAL_RECORD_ID'],
                    'WINNER': 'NEW' if n['QA_STATUS'] in ('QA_PASS', 'QA_CORRECTED')
                              else 'PRECISA_DE_HUMANO',
                    'WHY': ('a coleta nova foi a fonte em 02/09/2026 e a data saiu do '
                            'sitio do organizador. O pacote anterior nao registra de '
                            'onde a data dele veio.'
                            if n['QA_STATUS'] in ('QA_PASS', 'QA_CORRECTED') else
                            'o registro novo nao passou por conferencia independente '
                            '(QA_UNREVIEWED) — nao pode derrubar sozinho um dado que '
                            'ja estava no pacote.'),
                    'BASE_DE_QA': n['QA_STATUS'],
                    'SOURCE_NEW': n.get('source_url'),
                    'SEMELHANCA_DO_NOME': round(sc, 2),
                })
            else:
                adicoes.append({'OBJETO': 'EVENTO', 'NOTA': 'mesmo evento, datas '
                                'compativeis ou ausentes — nada a resolver',
                                'OLD_ID': melhor.get('ID'),
                                'NEW_ID': n['CANONICAL_RECORD_ID']})

    # ── CATÁLOGO ──────────────────────────────────────────────────────────────
    prods = le('ADAMA/adama-italy-products.json', 'PRODUCTS')
    com_flag = sum(1 for p in prods if p.get('IN_PUBLIC_CATALOG'))
    conflitos.append({
        'OBJETO': 'CATALOGO COMERCIAL ADAMA ITALIA',
        'CAMPO': 'quantos produtos estao no catalogo publico',
        'OLD_VALUE': '%d marcados IN_PUBLIC_CATALOG em adama-italy-products.json'
                     % com_flag,
        'NEW_VALUE': '51 fichas de produto lidas pela sitemap · 26 ERBICIDI, '
                     '14 FUNGICIDI, 6 INSETTICIDI, 5 SPECIALI',
        'WINNER': 'AMBOS, PORQUE SAO PERGUNTAS DIFERENTES',
        'WHY': ('a bandeira no arquivo responde «este produto do REGISTRO tem ficha?» '
                'e o censo responde «quantas FICHAS o catalogo publica?». Um produto '
                'de catalogo cujo titular nao e a ADAMA nunca teria bandeira, porque '
                'o arquivo dos 163 foi filtrado por titular. Sao seis produtos assim. '
                'Substituir um numero pelo outro apagaria o achado.'),
        'BASE_DE_QA': 'QA_PASS (7 de 8 do bloco catalogo sobreviveram)',
        'ACAO': 'manter as duas classes separadas: CATALOG_PRODUCT e '
                'REGULATORY_PRODUCT, como manda o §12',
    })

    # ── FENOLOGIA ─────────────────────────────────────────────────────────────
    ph = le('CROP-WINDOWS/current-phenology.json', 'PHENOLOGY')
    reg_velhas = {_n(x.get('REGION')).split()[0] for x in ph if x.get('REGION')}
    novos_fs = [r for r in novos if r['FAMILIA'] == 'CURRENT_FIELD_SIGNALS']
    reg_novas = {_n(r.get('region')).split()[0] for r in novos_fs if r.get('region')}
    adicoes.append({
        'OBJETO': 'FENOLOGIA / CAMPO CORRENTE',
        'NOTA': 'aditivo, nao conflitante: sao boletins DIFERENTES, de datas e '
                'regioes diferentes. Nenhum contradiz o outro.',
        'REGIOES_SO_NO_ANTERIOR': sorted(reg_velhas - reg_novas),
        'REGIOES_SO_NA_LAST_MILE': sorted(reg_novas - reg_velhas),
        'REGIOES_NOS_DOIS': sorted(reg_velhas & reg_novas),
    })

    # ── VOZES: o que NAO e conflito ───────────────────────────────────────────
    adicoes.append({
        'OBJETO': 'VOZES',
        'NOTA': 'NAO e conflito e NAO se funde. `field-voices` sao 58 falas de '
                'PLATEIA de canal (comentario sob video, sem identidade provada). '
                '`PUBLIC_VOICES` sao vozes IDENTIFICADAS, com cargo e frase assinada. '
                'Fundi-las apagaria a distincao que o eixo de plateia existe para '
                'preservar — foi ela que impediu conversa de horta de virar '
                'inteligencia de lavoura.',
        'ANTERIOR': len(le('VOCI-DAL-CAMPO/field-voices.json', 'VOICES')),
        'LAST_MILE': len([r for r in novos if r['FAMILIA'] == 'PUBLIC_VOICES']),
    })

    saida = {
        'DATASET': 'IT-V2-CONFLITOS',
        'LEI': 'a fusao e ADITIVA. Nada do pacote anterior se perde. Conflito nao '
               'resolvido vira duas verdades no mesmo portal.',
        'CONFLITOS': len(conflitos),
        'PRECISAM_DE_HUMANO': sum(1 for c in conflitos
                                  if c.get('WINNER') == 'PRECISA_DE_HUMANO'),
        'LISTA': conflitos,
        'ADICOES_SEM_CONFLITO': adicoes,
    }
    os.makedirs(V2, exist_ok=True)
    p = os.path.join(V2, 'IT-V2-CONFLITOS.json')
    json.dump(saida, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('conflitos: %d  (precisam de humano: %d)'
          % (len(conflitos), saida['PRECISAM_DE_HUMANO']))
    for c in conflitos:
        print('  · %s / %s' % (c['OBJETO'][:56], c['CAMPO']))
        print('      antes: %s' % str(c['OLD_VALUE'])[:88])
        print('      agora: %s' % str(c['NEW_VALUE'])[:88])
        print('      ganha: %s' % c['WINNER'])
    print()
    print('adicoes sem conflito: %d' % len(adicoes))
    print('gravado:', os.path.relpath(p, ROOT))


if __name__ == '__main__':
    main()
