#!/usr/bin/env python3
"""
DUAS CAMADAS QUE NUNCA VIRAM UMA — resposta registrada x atividade paga na Meta.

    COMPETITOR_REGISTERED_RESPONSE
        o concorrente TEM produto autorizado naquele pais. Vem do registro
        nacional. Diz o que ele PODE vender.

    COMPETITOR_PAID_META_ACTIVITY
        o concorrente ESTA (ou esteve) anunciando de forma observavel na Meta.
        Vem da Biblioteca de Anuncios. Diz o que ele esta FALANDO.

As duas respondem perguntas diferentes, e a missao pede que continuem separadas.
Este arquivo cruza sem fundir: cada empresa x pais recebe uma celula da matriz,
e a celula tem NOME, nao nota.

    RESPONSE=YES  ACTIVATION=YES   tem registro e esta anunciando
    RESPONSE=YES  ACTIVATION=NO    tem registro e nao vimos anuncio
    RESPONSE=NO   ACTIVATION=YES   anuncia, e nao achamos registro
    RESPONSE=NOT_KNOWN ...         nao olhamos aquele pais no registro

A CELULA MAIS PERIGOSA E A TERCEIRA
------------------------------------
`RESPONSE=NOT_PROVED + ACTIVATION=YES` NAO significa "esta anunciando produto
sem registro". Significa que a nossa cobertura regulatoria daquele pais nao
alcanca aquela empresa. Confundir os dois transformaria um buraco do nosso
acervo em acusacao sobre um concorrente. Por isso o estado se chama
`REGISTRO_NAO_CONSULTADO` quando nao ha fonte carregada para o pais, e
`REGISTRO_CONSULTADO_SEM_ACHADO` quando ha — e sao duas coisas diferentes.

    NAO_ENCONTREI != NAO_EXISTE
    ANUNCIO_OBSERVADO != PRODUTO_AUTORIZADO

O CRUZAMENTO POR PRODUTO
-------------------------
Um produto do anuncio so casa com um produto do registro se o NOME BATER apos
normalizacao simples. Nada de semelhanca aproximada aqui: "MAXENTIS" e
"MAXENTIS" casam; "Amistar" e "AMISTAR ERA 240 EC" nao casam sozinhos, e sair
`PRODUCT_MATCH_NOT_PROVED` e a resposta certa, nao uma falha.
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
SAMPLES = os.path.join(ROOT, 'data', 'samples')
DEST = os.path.join(PASTA, 'META-CONVERGENCE-RESPONSE-VS-ACTIVITY-V1.json')

# Fontes de RESPOSTA REGISTRADA ja existentes neste acervo. A lista e declarada
# a mao de proposito: carregar "tudo que parecer registro" traria arquivo de
# outra camada e o cruzamento passaria a misturar o que nao deve.
FONTES_REGISTRO = [
    {'arquivo': 'COMPETITOR-azoxy-prothio-italy.json', 'country': 'IT',
     'campo_produtos': 'products_in_force', 'campo_empresa': 'company',
     'campo_nome': 'product'},
]

SIM = 'YES'
NAO_PROVADO = 'NOT_PROVED'
NAO_CONSULTADO = 'REGISTRO_NAO_CONSULTADO'
CONSULTADO_SEM_ACHADO = 'REGISTRO_CONSULTADO_SEM_ACHADO'
PRODUCT_MATCH_PROVED = 'PRODUCT_MATCH_PROVED'
PRODUCT_MATCH_NOT_PROVED = 'PRODUCT_MATCH_NOT_PROVED'


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').upper())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9 ]+', ' ', s).strip()


def _empresa_base(nome):
    """'ADAMA ITALIA S.R.L.' -> 'ADAMA'. So corta sufixo societario conhecido."""
    n = norm(nome)
    n = re.sub(r'\b(S R L|SRL|S P A|SPA|GMBH|AG|SA|SAS|BV|LTD|INC|ESPANA|ITALIA|'
               r'FRANCE|IBERIA|AGRICULTURAL SOLUTIONS|CROP SCIENCE|AGRO)\b', ' ', n)
    return re.sub(r'\s+', ' ', n).strip()


def carregar_registro(fontes=FONTES_REGISTRO):
    """Devolve {(empresa_base, country): [produtos]} e os paises consultados."""
    mapa, paises = {}, set()
    for f in fontes:
        caminho = os.path.join(SAMPLES, f['arquivo'])
        if not os.path.exists(caminho):
            continue
        with open(caminho, encoding='utf-8') as fh:
            d = json.load(fh)
        paises.add(f['country'])
        for p in d.get(f['campo_produtos'], []):
            emp = _empresa_base(p.get(f['campo_empresa']))
            if not emp:
                continue
            mapa.setdefault((emp, f['country']), []).append({
                'product_name': p.get(f['campo_nome']),
                'registration': p.get('reg'),
                'status': p.get('status'),
                'source_file': f['arquivo'],
            })
    return mapa, paises


def carregar_atividade(arquivo):
    """Agrega o acervo de anuncios por (empresa_base, pais alcancado)."""
    if not os.path.exists(arquivo):
        return {}
    with open(arquivo, encoding='utf-8') as f:
        d = json.load(f)
    saida = {}
    for e in (d.get('entities') or {}).values():
        emp = _empresa_base(e.get('company'))
        for pais in (e.get('countries_reached_observed') or []):
            k = (emp, pais)
            a = saida.setdefault(k, {'ads': 0, 'active': 0, 'products': set(),
                                     'library_ids': []})
            a['ads'] += 1
            if e.get('active_status') == 'ACTIVE':
                a['active'] += 1
            for p in ((e.get('reading') or {}).get('product_candidates') or []):
                if p.get('state') == 'PROVED':
                    a['products'].add(norm(p['product_name']))
            if len(a['library_ids']) < 5:
                a['library_ids'].append(e.get('meta_ad_library_id'))
    return saida


def cruzar(registro, paises_consultados, atividade):
    celulas = []
    chaves = set(registro) | set(atividade)
    for emp, pais in sorted(chaves):
        reg = registro.get((emp, pais))
        ati = atividade.get((emp, pais))
        if reg:
            resposta = SIM
        elif pais in paises_consultados:
            resposta = CONSULTADO_SEM_ACHADO
        else:
            resposta = NAO_CONSULTADO
        ativacao = SIM if ati else NAO_PROVADO

        casados = []
        if reg and ati:
            nomes_reg = {norm(p['product_name']): p for p in reg}
            for prod in sorted(ati['products']):
                if prod in nomes_reg:
                    casados.append({'product': prod,
                                    'state': PRODUCT_MATCH_PROVED,
                                    'registration': nomes_reg[prod]['registration']})
        celulas.append({
            'company_base': emp,
            'country': pais,
            'competitor_registered_response': resposta,
            'competitor_paid_meta_activity': ativacao,
            'cell': 'RESPONSE=%s / ACTIVATION=%s' % (resposta, ativacao),
            'registered_products': reg or [],
            'ads_observed': (ati or {}).get('ads', 0),
            'ads_active_observed': (ati or {}).get('active', 0),
            'evidence_library_ids': (ati or {}).get('library_ids', []),
            'product_crosscheck': casados or [{'state': PRODUCT_MATCH_NOT_PROVED}],
            'nota': ('celula, nao nota. RESPONSE e ACTIVATION respondem perguntas '
                     'diferentes e nao se substituem.'),
        })
    return celulas


def rodar(arquivo_atividade=None):
    arquivo_atividade = arquivo_atividade or os.path.join(
        PASTA, 'META-ADS-ENTITIES-EAME-V1.json')
    registro, paises = carregar_registro()
    atividade = carregar_atividade(arquivo_atividade)
    celulas = cruzar(registro, paises, atividade)
    saida = {
        'dataset_owner': 'META_COMPETITOR_EAME',
        'countries_with_registration_source_loaded': sorted(paises),
        'registration_sources': [f['arquivo'] for f in FONTES_REGISTRO],
        'cells': celulas,
        'limitacoes': [
            'A cobertura regulatoria carregada aqui e minima: %s. Pais fora '
            'dessa lista sai REGISTRO_NAO_CONSULTADO, que nao e "sem registro".'
            % (sorted(paises) or 'nenhum'),
            'ACTIVATION=NOT_PROVED significa que NAO VIMOS anuncio por esta rota, '
            'nunca que a empresa nao anuncia.',
            'O cruzamento por produto exige nome igual apos normalizacao. Nada de '
            'semelhanca aproximada — casar por parecenca inventaria autorizacao.',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    return saida


if __name__ == '__main__':
    r = rodar(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({'celulas': len(r['cells']),
                      'paises_com_registro': r['countries_with_registration_source_loaded']},
                     ensure_ascii=False))
    for c in r['cells'][:12]:
        print('  %-14s %s  %s' % (c['company_base'], c['country'], c['cell']))
