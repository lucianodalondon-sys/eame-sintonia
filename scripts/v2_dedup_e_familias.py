#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEDUPLICA os 321 registros e os separa nas DEZ FAMÍLIAS do §10.

    python3 scripts/v2_dedup_e_familias.py

§6 · UMA OBSERVAÇÃO DO MUNDO REAL NÃO VIRA DOIS FATOS
------------------------------------------------------
Os dois fluxos de coleta se sobrepuseram de propósito: o segundo foi às mesmas
regiões pela rota italiana. O boletim VITE n.20 do Vêneto foi colhido duas
vezes, por dois agentes diferentes, e virou dois registros.

A chave canônica é a que a missão manda: FONTE · DATA · CULTURA · PROBLEMA ·
REGIÃO · TIPO DE FATO. Igual nos seis → é o MESMO fato.

⚠️ E A REGRA DE QUEM SOBREVIVE
-------------------------------
Não é o primeiro nem o mais completo. É o de MELHOR QA:

    QA_CORRECTED > QA_PASS > QA_UNREVIEWED > QA_REJECTED

Porque um registro corrigido pela conferência é, por construção, o único que
alguém conferiu na fonte. Manter o cru ao lado dele seria manter viva a versão
que já se sabe errada — que é exatamente o que o §5 proíbe.

A linhagem inteira fica: `RAW_RECORD_IDS` guarda todos os que colapsaram, e
`CANONICAL_RECORD_ID` é o que ficou. Ninguém perde o rastro de onde veio.

§10 · AS FAMÍLIAS NÃO SE ACHATAM NUMA TABELA SÓ
------------------------------------------------
«Do not flatten them into one generic records table only.» Preço, boletim,
clima e voz têm semânticas diferentes — e foi justamente misturar semântica
que fez o demo apresentar conversa de horta como inteligência de lavoura.
"""
import hashlib
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, 'data', 'samples', 'IT-V2')

# bloco de coleta → família canônica do §10
FAMILIA = {
    'fenologia': 'CURRENT_FIELD_SIGNALS',
    'boletins-regioes-fechadas': 'CURRENT_FIELD_SIGNALS',
    'mercado': 'MARKET_OBSERVATIONS',
    'ismea-mercado': 'MARKET_OBSERVATIONS',
    'peso-economico': 'CROP_ECONOMIC_WEIGHT',
    'istat-area-producao': 'CROP_ECONOMIC_WEIGHT',
    'catalogo': 'COMMERCIAL_CATALOG',
    'regulatorio': 'REGULATORY_FUTURE',
    'clima': 'AGROMET_CONDITIONS',
    'arpav-clima-veneto': 'AGROMET_CONDITIONS',
    'concorrente': 'COMPETITOR_PUBLIC_SIGNALS',
    'vozes': 'PUBLIC_VOICES',
    'herbicida': 'HERBICIDE_CURRENT_CONTEXT',
    'eventos': 'FUTURE_EVENTS',
}

ORDEM_QA = {'QA_CORRECTED': 0, 'QA_PASS': 1, 'PENDENTE_DE_DECISAO': 2,
            'QA_UNREVIEWED': 3, 'QA_REJECTED': 9}


def _n(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', str(t or ''))
                if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


def host(url):
    m = re.match(r'https?://([^/]+)', str(url or ''))
    return (m.group(1) if m else '').lower().replace('www.', '')


def tipo_de_fato(r):
    """A NATUREZA do fato, não o texto. `PRECO` e `preco medio` são o mesmo."""
    t = _n(r.get('tipo'))
    for chave, marca in (
            ('preco prezzo prezzi quotazion cotac', 'PRECO'),
            ('superficie area ettar produzion resa rendiment', 'AREA_PRODUCAO'),
            ('boletim bollettino fenolog bbch fase', 'FENOLOGIA'),
            ('chuva temperatur pioggia clima meteo seca siccit umid', 'CLIMA'),
            ('aprovac renovac substanc regulat scopaff efsa', 'REGULATORIO'),
            ('evento fiera convegno giornate congress', 'EVENTO'),
            ('voz voce dichiaraz intervista declarac', 'VOZ'),
            ('concorrent competitor lancament campanha', 'CONCORRENTE'),
            ('diserbo erbicid infestant daninha malerb', 'HERBICIDA'),
            ('catalogo prodotto produto ficha', 'CATALOGO')):
        if any(w in t for w in chave.split()):
            return marca
    return 'OUTRO'


def chave_canonica(r):
    """§6 · FONTE · DATA · CULTURA · PROBLEMA · REGIÃO · TIPO DE FATO.

    ⚠️ O «PROBLEMA» entra pelo texto do fato, e isso NÃO é preguiça — é o que
    impede a fusão errada. Medido: sem ele, 17 grupos casariam, e ao abrir um
    por um se vê que quase nenhum é duplicata:

        boletim VITE do Vêneto, 27/08 → um registro é a FASE FENOLÓGICA,
        o outro é a RECOMENDAÇÃO de controle da flavescência. Mesmo documento,
        mesma cultura, mesma data, mesma região — dois fatos.

        ISMEA frumento tenero → um é «preço médio por produto», o outro é
        «preço médio por qualidade». Dois recortes da mesma página.

        ARPAE 24/08 → um é chuva acumulada, o outro é água no solo.

    Fundir isso perderia metade da informação e criaria um fato que ninguém
    publicou.

        DOIS FATOS DO MESMO DOCUMENTO NÃO SÃO O MESMO FATO.
        A duplicata que o §6 teme é a mesma OBSERVAÇÃO colhida duas vezes —
        não duas leituras diferentes da mesma página.
    """
    return '|'.join([
        host(r.get('source_url')),
        str(r.get('publication_date') or '')[:10],
        _n(r.get('crop'))[:26],
        _n(r.get('o_que'))[:44],
        _n(r.get('region'))[:26],
        tipo_de_fato(r),
    ])


# ── AS DUPLICATAS DE VERDADE, CONFERIDAS À MÃO ───────────────────────────────
# A busca por semelhança de citação devolveu 3 pares acima de 0,70. Abertos um
# a um, DOIS eram falso positivo — o ISMEA repete o cabeçalho da página em
# recortes diferentes, e a citação fica parecida sem o fato ser o mesmo.
#
#     UM LIMIAR QUE ERRA DOIS EM TRÊS NÃO É UM LIMIAR. É UM PALPITE.
#
# Então a fusão é declarada, não inferida. Cada par abaixo foi lido.
FUSOES_CONFERIDAS = [
    {
        'PAR': ('arsacweb.it|2026-08-25|vite|FENOLOGIA', 'ARSAC · vite · semana 35'),
        'POR_QUE': ('os dois registros descrevem a MESMA linha do boletim ARSAC da '
                    'semana 35: «mais de 90% dos vinhedos observados em fase de '
                    'maturação». Um fluxo a colheu como fenologia, o outro como '
                    'quantificador regional. Uma observação, dois registros.'),
        'CASA_POR': lambda a, b: (
            'arsacweb' in host(a.get('source_url'))
            and 'arsacweb' in host(b.get('source_url'))
            and _n(a.get('crop'))[:4] == 'vite' == _n(b.get('crop'))[:4]
            and str(a.get('publication_date'))[:10] == str(b.get('publication_date'))[:10]),
    },
]


def main():
    d = json.load(open(os.path.join(V2, 'IT-V2-QA-ATRIBUIDO.json'), encoding='utf-8'))
    regs = d['REGISTROS']

    # id estável por conteúdo, para a linhagem não depender de ordem
    for r in regs:
        semente = '%s|%s|%d' % (r['BLOCO'], r.get('source_url'), r['INDICE_NO_BLOCO'])
        r['RAW_RECORD_ID'] = 'IT-RAW-' + hashlib.sha1(
            semente.encode('utf-8')).hexdigest()[:10].upper()
        r['FAMILIA'] = FAMILIA.get(r['BLOCO'], 'OUTRA')
        r['TIPO_DE_FATO'] = tipo_de_fato(r)
        r['CHAVE_CANONICA'] = chave_canonica(r)

    grupos = defaultdict(list)
    for r in regs:
        grupos[r['CHAVE_CANONICA']].append(r)

    # ── as fusões conferidas à mão, aplicadas sobre os grupos ────────────────
    fundidos = []
    for f in FUSOES_CONFERIDAS:
        alvo = [k for k, v in grupos.items() for x in v
                if any(f['CASA_POR'](x, y) for kk, vv in grupos.items()
                       if kk != k for y in vv)]
        alvo = sorted(set(alvo))
        if len(alvo) > 1:
            juntos = [x for k in alvo for x in grupos[k]]
            for k in alvo[1:]:
                del grupos[k]
            grupos[alvo[0]] = juntos
            fundidos.append({'CHAVES': alvo, 'N': len(juntos),
                             'POR_QUE': f['POR_QUE']})

    canonicos, colapsados = [], 0
    for chave, itens in grupos.items():
        itens.sort(key=lambda x: (ORDEM_QA.get(x['QA_STATUS'], 5),
                                  -len(json.dumps(x, ensure_ascii=False))))
        ganhador = itens[0]
        outros = itens[1:]
        colapsados += len(outros)
        cid = 'IT-CAN-' + hashlib.sha1(chave.encode('utf-8')).hexdigest()[:10].upper()
        canonicos.append(dict(
            ganhador,
            CANONICAL_RECORD_ID=cid,
            RAW_RECORD_IDS=[x['RAW_RECORD_ID'] for x in itens],
            COLAPSOU_N=len(outros),
            COLAPSOU_DE_BLOCOS=sorted({x['BLOCO'] for x in itens}),
            QA_DOS_COLAPSADOS=sorted({x['QA_STATUS'] for x in outros}) or None,
            POR_QUE_ESTE_GANHOU=(
                'unico registro desta chave' if not outros else
                'melhor estado de QA entre %d registros da mesma chave canonica '
                '(%s). Os outros ficam na linhagem, nao no feed.'
                % (len(itens), ' > '.join(x['QA_STATUS'] for x in itens))),
        ))

    por_fam = Counter(r['FAMILIA'] for r in canonicos)
    por_qa = Counter(r['QA_STATUS'] for r in canonicos)
    multi = [r for r in canonicos if r['COLAPSOU_N']]

    saida = {
        'DATASET': 'IT-V2-CANONICO',
        'LEI_DA_CHAVE': 'FONTE · DATA · CULTURA · PROBLEMA · REGIAO · TIPO DE FATO',
        'LEI_DE_QUEM_SOBREVIVE':
            'QA_CORRECTED > QA_PASS > PENDENTE > QA_UNREVIEWED. Nao e o primeiro '
            'nem o mais completo: e o que alguem conferiu na fonte.',
        'LEI_DA_FAMILIA':
            'as dez familias nao se achatam numa tabela so. Preco, boletim, clima e '
            'voz tem semanticas diferentes, e misturar semantica foi o que fez o '
            'demo apresentar conversa de horta como inteligencia de lavoura.',
        'BRUTOS': len(regs),
        'CANONICOS': len(canonicos),
        'COLAPSADOS': colapsados,
        'CHAVES_COM_MAIS_DE_UM': len(multi),
        'FUSOES_CONFERIDAS_A_MAO': fundidos,
        'POR_QUE_TAO_POUCA_FUSAO':
            'a missao esperava sobreposicao entre os dois fluxos, e ela existe '
            'no nivel do DOCUMENTO: 14 URLs foram lidas por mais de um bloco. '
            'Mas ao abrir cada caso, os registros descrevem FATOS DIFERENTES do '
            'mesmo documento -- fase fenologica x recomendacao de controle, '
            'preco por produto x preco por qualidade, chuva x agua no solo. '
            'Fundir teria perdido metade da informacao.',
        'POR_FAMILIA': dict(por_fam),
        'POR_QA': dict(por_qa),
        'REGISTROS': canonicos,
    }
    p = os.path.join(V2, 'IT-V2-CANONICO.json')
    json.dump(saida, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('brutos: %d → canonicos: %d  (colapsados: %d, em %d chaves)'
          % (len(regs), len(canonicos), colapsados, len(multi)))
    print()
    print('por familia:')
    for k, v in por_fam.most_common():
        print('  %-30s %d' % (k, v))
    print()
    print('por QA:', dict(por_qa))
    if multi:
        print()
        print('exemplos de colapso:')
        for r in multi[:5]:
            print('  %s ← %d registros de %s'
                  % (r['CANONICAL_RECORD_ID'], len(r['RAW_RECORD_IDS']),
                     ', '.join(r['COLAPSOU_DE_BLOCOS'])))
            print('     %s' % (r.get('o_que') or '')[:88])
    print()
    print('gravado:', os.path.relpath(p, ROOT))


if __name__ == '__main__':
    main()
