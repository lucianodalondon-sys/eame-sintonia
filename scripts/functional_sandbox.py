# -*- coding: utf-8 -*-
"""FUNCTIONAL_SANDBOX — PROTOTYPE_ONLY. Nao e o casco, nao e V8, nao e ferramenta.

Coloca as capacidades novas na dinamica que o casco V7 ja define para um caso:

    CASE -> CAMADAS -> CONVERGENCIAS -> CRUZAMENTOS -> TEMPO -> MAPA DE ACAO

e mostra, para um recorte real, O QUE ACENDE e O QUE CONTINUA `NAO SEI`.

Nao escreve em banco, nao le rede, nao toca no casco, nao publica ferramenta.
Imprime texto. A saida serve para decidir DEPOIS — no red team e na arbitragem —
se a capacidade merece superficie propria, camada de caso, ou nenhuma das duas.

    py scripts/functional_sandbox.py
    py scripts/functional_sandbox.py --json
"""
import json
import os
import sys

# O console do Windows abre em cp1252 e alguns nomes reais trazem hifen tipografico
# (U+2010) — "Mercado‐Blanco" derruba o print. O dado esta certo; e a saida que precisa
# aguentar. Nunca trocar o dado para caber no terminal.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:  # pragma: no cover — interpretador antigo
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import functional_prep as fp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, 'data', 'functional-sandbox', 'fixtures')

# As sete camadas de evidencia que o casco V7 declara no detalhe de caso.
CAMADAS_DO_CASCO = ('Campo', 'Ciencia', 'Clima', 'Regulatorio',
                    'Portfolio local ADAMA', 'Competicao', 'Tempo')

# Recortes reais, tirados dos seis congelados pela arbitra.
RECORTES = (
    {'CASE_ID': 'ES-OLIVE-REPILO', 'COUNTRY': 'ES', 'CROP': 'OLIVE', 'ISSUE': 'REPILO'},
    {'CASE_ID': 'IT-VINE-FLAVESCENCE', 'COUNTRY': 'IT', 'CROP': 'GRAPEVINE', 'ISSUE': 'FLAVESCENCE'},
    {'CASE_ID': 'FR-CEREAL-SEPTORIA', 'COUNTRY': 'FR', 'CROP': 'CEREALS', 'ISSUE': 'SEPTORIA'},
)


def _carregar_tudo():
    creators = fp.adaptar_creator_capability(
        fp.carregar(os.path.join(FIX, 'creator-capability-sample.json')))
    contas = fp.adaptar_public_comm(
        fp.carregar(os.path.join(FIX, 'public-comm-batch-sample.json')))
    experts = fp.adaptar_expert_directory(
        fp.carregar(os.path.join(ROOT, 'data', 'samples', 'SPEAKER-UNIVERSE-PILOT-V1.json')))
    return creators, contas, experts


def _crops_do_objeto(o):
    cp = o['FIELDS'].get('CROP_PROOF') or {}
    return set(cp.get('CROPS') or [])


def montar(recorte, creators, contas, experts):
    """Monta a leitura de UM recorte. Nada aqui vira score."""
    pais = recorte['COUNTRY']
    cultura = recorte['CROP']

    # --- CREATOR: pessoa e empresa contadas SEPARADAS, sempre
    do_pais = [o for o in creators if o['COUNTRY'] == pais]
    da_cultura = [o for o in do_pais if cultura in _crops_do_objeto(o)]
    prontos = [o for o in da_cultura if o['FIELDS'].get('ACTIVATION_STATE') == 'ACTIVATION_READY']
    pessoas = [o for o in prontos if o['ANALYTICAL_UNIT'] == 'PERSON']
    empresas = [o for o in prontos if o['ANALYTICAL_UNIT'] == 'FARM_BUSINESS_ENTITY']

    # --- EXPERT: ligado pelo CASE_ID, que e a chave que a fonte declara
    peritos = [o for o in experts if o['FIELDS'].get('CASE_ID') == recorte['CASE_ID']]

    # --- PUBLIC COMM: conta local, nunca "a empresa"
    contas_pais = [o for o in contas if o['COUNTRY'] == pais]
    empresas_com_conta = sorted(set(o['FIELDS']['COMPANY'] for o in contas_pais))

    camadas = dict((c, 'NAO MEDIDO') for c in CAMADAS_DO_CASCO)
    camadas['Ciencia'] = 'PARCIAL — %d pessoa(s) com identidade provada' % len(peritos) if peritos else 'NAO MEDIDO'
    if contas_pais:
        camadas['Competicao'] = ('PARCIAL — %d conta(s) local(is) provada(s), '
                                 'CONTEUDO NAO COLETADO' % len(contas_pais))
    camadas['Tempo'] = 'NAO CONECTADO'

    return {
        'CASE_ID': recorte['CASE_ID'],
        'COUNTRY': pais,
        'CROP': cultura,
        'ISSUE': recorte['ISSUE'],
        'CAMADAS_DO_CASCO': camadas,
        'CAMADA_NOVA_AUDIENCIA_ATIVACAO': {
            'PERSON_CREATOR_ACTIVATION_READY': len(pessoas),
            'FARM_BUSINESS_PARTNER_READY': len(empresas),
            'NUNCA_SOMAR': 'pessoa != empresa; a soma nao se chama CREATORS_READY',
            'PESSOAS': [o['FIELDS']['DISPLAY_NAME'] for o in pessoas],
            'EMPRESAS': [o['FIELDS']['DISPLAY_NAME'] for o in empresas],
            'O_QUE_ISTO_NAO_PROVA': ['FIELD_PROBLEM', 'INCIDENCE',
                                     'MARKET_OPPORTUNITY', 'PRODUCT_FIT'],
        },
        'CAMADA_CIENCIA_PESSOAS': {
            'IDENTIDADE_PROVADA': len(peritos),
            'NOMES': [o['FIELDS']['NAME'] for o in peritos],
            'CANAL_PUBLICO': 'NAO VEM DESTE ARTEFATO',
            'CONTEUDO_LIGADO_A_PESSOA': 'NAO PROVADO PARA NINGUEM',
        },
        'CAMADA_COMPETICAO_COMUNICACAO': {
            'CONTAS_LOCAIS_PROVADAS': len(contas_pais),
            'EMPRESAS_COM_CONTA_LOCAL': empresas_com_conta,
            'CONTEUDO': 'NOT_COLLECTED — nenhuma coleta executada',
            'ZERO_SIGNIFICA': 'NO_CONTENT_COLLECTION_EXECUTED, nunca COMPANY_NOT_COMMUNICATING',
            'ATIVACAO_PAGA_META': 'NAO TESTADO — camada separada, nunca somada a esta',
        },
        'CONVERGENCIA': {
            'PERNAS_COM_EVIDENCIA_INDEPENDENTE': sum(
                1 for v in (peritos, contas_pais) if v),
            'REGRA': 'contagem de pernas NUNCA vira score; independencia precisa ser provada',
            'O_QUE_FALTA_PARA_FECHAR': 'campo datado, portfolio local ligado ao par, e tempo',
        },
        'TEMPO': {
            'JANELA_AGRONOMICA': 'NAO CONECTADA',
            'JANELA_DE_DECISAO': 'NAO DETERMINADA',
            'POR_QUE': 'nenhuma das tres capacidades novas entrega relogio de lavoura',
        },
        'MAPA_DE_ACAO': {
            'MARKETING': ('pode avaliar %d pessoa(s) e %d empresa(s)'
                          % (len(pessoas), len(empresas))) if prontos else 'nada a avaliar neste recorte',
            'TECNICO_CIENCIA': ('pode consultar %d especialista(s) com identidade provada'
                                % len(peritos)) if peritos else 'nenhum especialista neste recorte',
            'MARKET_DEVELOPMENT': 'AREA CENTRAL — avalia e programa a investigacao',
            'REGULATORIO': 'NAO DETERMINADO nesta preparacao',
            'PORTFOLIO': 'NAO DETERMINADO nesta preparacao',
            'COMERCIAL': 'NAO DETERMINADO nesta preparacao',
            'SUPPLY': 'NAO SE APLICA — sem evidencia que torne a area relevante',
        },
        'WIRED_TO_CASCO': False,
        'MODE': 'PROTOTYPE_ONLY',
    }


def rodar():
    creators, contas, experts = _carregar_tudo()
    return {
        'SANDBOX': 'FUNCTIONAL_SANDBOX',
        'MODE': 'PROTOTYPE_ONLY',
        'CASCO_V7_MODIFIED': False,
        'REAL_DATA_WIRED': False,
        'TOTAIS': {
            'CREATOR_OBJECTS': fp.contar(creators),
            'PUBLIC_COMM_OBJECTS': fp.contar(contas),
            'EXPERT_OBJECTS': fp.contar(experts),
        },
        'RECORTES': [montar(r, creators, contas, experts) for r in RECORTES],
    }


def medicao():
    """Artefato de medicao DERIVADO — nenhum numero e digitado a mao.

    Se um artefato de origem mudar, este arquivo muda ao ser regerado, e a divergencia
    aparece no diff em vez de envelhecer calada dentro de um documento.
    """
    s = rodar()
    creators, contas, experts = _carregar_tudo()
    cap = fp.carregar(os.path.join(FIX, 'creator-capability-sample.json'))
    linhas_ar = cap['LOOKUP_BY_ACTIVATION_STATE']['ACTIVATION_READY']
    com_creator = [r for r in s['RECORTES']
                   if r['CAMADA_NOVA_AUDIENCIA_ATIVACAO']['PERSON_CREATOR_ACTIVATION_READY']
                   or r['CAMADA_NOVA_AUDIENCIA_ATIVACAO']['FARM_BUSINESS_PARTNER_READY']]
    return {
        'SOURCE_ID': 'FUNCTIONAL-SANDBOX/PREP-MEDICAO',
        'source': 'derivado dos adaptadores sobre fixtures reais — nenhuma coleta, custo zero',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'n/a — descreve o acervo, nao o mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'captured_at': '2026-08-30',
        'CAPTURED_AT': '2026-08-30',
        'MODE': 'PROTOTYPE_ONLY',
        'CASCO_V7_MODIFIED': False,
        'REAL_DATA_WIRED': False,
        'PRODUCT_IMPLEMENTATION_MODE': 'NOT_ENTERED',
        'COMO_REPRODUZIR': 'py scripts/functional_sandbox.py --medicao',
        'OBJETOS_POR_CAPACIDADE': s['TOTAIS'],
        'CARDINALIDADE_PERIGOSA': {
            'ONDE': 'CREATOR_CAPABILITY.LOOKUP_BY_ACTIVATION_STATE.ACTIVATION_READY',
            'LINHAS': len(linhas_ar),
            'ENTIDADES': len(set(x['HANDLE'] for x in linhas_ar)),
            'FATOR_DE_INFLACAO': round(len(linhas_ar) / float(len(set(x['HANDLE'] for x in linhas_ar))), 2),
            'POR_QUE': 'a mesma pessoa aparece uma vez por cultura. Contar linha e contar cultura, nao gente.',
            'LEI': 'ROW != ENTITY',
        },
        'CONTA_NAO_E_EMPRESA': {
            'CONTAS_LOCAIS': len(contas),
            'EMPRESAS_DISTINTAS': len(set(o['FIELDS']['COMPANY'] for o in contas)),
            'LEI': 'COMPANY_LOCAL_ACCOUNT != COMPANY',
        },
        'RECORTES_TESTADOS': len(s['RECORTES']),
        'RECORTES_COM_CREATOR_PRONTO': len(com_creator),
        'RECORTES_SEM_CREATOR_PRONTO': [r['CASE_ID'] for r in s['RECORTES'] if r not in com_creator],
        'O_QUE_ISTO_SUGERE': ('creator pronto e caso aberto nao coincidem por acaso. '
                              'Em 2 dos 3 recortes congelados nao ha creator pronto nenhum. '
                              'E medicao, nao veredito — a decisao entre ferramenta propria e '
                              'camada de caso pertence a arbitragem.'),
        'CAPACIDADE_SEM_ARTEFATO': {
            'COMPETITOR_FORESIGHT': 'NO_ARTIFACT_IN_REPO — adaptar_foresight() falha fechado',
        },
        'RECORTES': s['RECORTES'],
    }


def main():
    saida = rodar()
    if '--medicao' in sys.argv:
        destino = os.path.join(ROOT, 'data', 'functional-sandbox', 'PREP-MEDICAO.json')
        with open(destino, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(medicao(), f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('gravado %s' % destino)
        return 0
    if '--json' in sys.argv:
        print(json.dumps(saida, ensure_ascii=False, indent=1))
        return 0
    print('FUNCTIONAL_SANDBOX — PROTOTYPE_ONLY · casco nao tocado, nada ligado\n')
    for k, v in saida['TOTAIS'].items():
        print('  %-22s linhas=%-4d entidades=%-4d  %s'
              % (k, v['ROWS'], v['ENTITIES'], v['BY_ANALYTICAL_UNIT']))
    for r in saida['RECORTES']:
        print('\n' + '=' * 74)
        print('%s   %s x %s x %s' % (r['CASE_ID'], r['COUNTRY'], r['CROP'], r['ISSUE']))
        print('-- camadas do casco')
        for c, e in r['CAMADAS_DO_CASCO'].items():
            print('     %-24s %s' % (c, e))
        a = r['CAMADA_NOVA_AUDIENCIA_ATIVACAO']
        print('-- camada nova: audiencia / ativacao')
        print('     pessoas prontas  %d  %s' % (a['PERSON_CREATOR_ACTIVATION_READY'], a['PESSOAS']))
        print('     empresas prontas %d  %s' % (a['FARM_BUSINESS_PARTNER_READY'], a['EMPRESAS']))
        c = r['CAMADA_CIENCIA_PESSOAS']
        print('-- ciencia e pessoas')
        print('     identidade provada %d  %s' % (c['IDENTIDADE_PROVADA'], c['NOMES']))
        print('     canal publico: %s' % c['CANAL_PUBLICO'])
        k = r['CAMADA_COMPETICAO_COMUNICACAO']
        print('-- competicao / comunicacao publica')
        print('     contas locais provadas %d  %s' % (k['CONTAS_LOCAIS_PROVADAS'],
                                                      k['EMPRESAS_COM_CONTA_LOCAL']))
        print('     conteudo: %s' % k['CONTEUDO'])
        print('-- tempo')
        print('     janela agronomica %s · janela de decisao %s'
              % (r['TEMPO']['JANELA_AGRONOMICA'], r['TEMPO']['JANELA_DE_DECISAO']))
    print('\nPRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
