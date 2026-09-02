#!/usr/bin/env python3
"""
MEDIÇÃO DO PRIMEIRO LOTE E HANDOFF — o rendimento antes da ampliação.

    py scripts/comunicacao_medir.py

O §17 MANDA PARAR E MEDIR
--------------------------
A pergunta que este arquivo responde não é "quantos itens temos". É:

    VALE A PENA AMPLIAR PARA OS DEMAIS CONCORRENTES?

Por isso ele mede o funil inteiro — casas tentadas, contas achadas, contas provadas,
contas autorizadas, itens coletados — e não só a última linha. Uma missão que só publica
o total de itens não consegue dizer onde perdeu, e sem isso a decisão de ampliar é palpite.

AS TRÊS AUSÊNCIAS SÃO DIFERENTES, E O RELATÓRIO NÃO PODE COLAPSAR
-------------------------------------------------------------------
    NOT_ATTEMPTED       não tentei (empresa fora do primeiro lote)
    NO_LINK_DECLARED    tentei, e o site oficial não declarou link
    NOT_ELIGIBLE        achei conta oficial, mas ela não entra no lote COMPANY x
                        COUNTRY — por PAÍS (global/desconhecido) ou por PAPEL (página
                        de marca). São dois eixos, e o relatório mostra qual foi
    COLLECTED_ZERO      coletei e a conta não publicou na janela

Só a última é sobre a EMPRESA. As três primeiras são sobre a NOSSA cobertura. Um número
único faria as quatro parecerem "a empresa não comunica", que é a leitura errada mais
cara possível — é a mesma lei que esta casa já escreveu como SOURCE FAILURE != ZERO.

O HANDOFF É OPCIONAL POR CONTRATO
-----------------------------------
O §15 diz: esta missão é AUXILIARY_NON_BLOCKING. O refresh continua esperando os três
handoffs obrigatórios (EARLY SIGNAL, META COMPETITOR, COMPETITOR FORESIGHT) e segue sem
este. Por isso o campo `OPTIONAL_REFRESH_INPUT` é calculado, nunca torcido: ele só sai
`READY` quando existe item coletado E classificado. Identidade resolvida, sozinha, não é
insumo de inteligência — é insumo de coleta.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM')
DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'
NAO_SEI = 'NOT_KNOWN'
PLATAFORMAS = ('YOUTUBE', 'INSTAGRAM', 'FACEBOOK', 'LINKEDIN')


def _ler(nome):
    caminho = os.path.join(SAIDA, nome)
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _conta(chave, itens):
    fora = {}
    for i in itens:
        v = i.get(chave)
        v = '+'.join(v) if isinstance(v, list) else v
        fora[v] = fora.get(v, 0) + 1
    return fora


def montar():
    universo = _ler('UNIVERSO-CONTAS-V1.json') or {}
    contas = _ler('CONTAS-V1.json') or {}
    classificado = _ler('CLASSIFICADO-V1.json') or {}

    todas = contas.get('ACCOUNTS') or []
    provadas = [c for c in todas if c['ACCOUNT_IDENTITY_STATE'] == 'PROVED']
    autorizadas = [c for c in todas if c['COLLECTION_AUTHORIZED'] == 'YES']
    rejeitadas = [c for c in todas if c['ACCOUNT_IDENTITY_STATE'] == 'REJECTED']
    oficiais_fora = [c for c in provadas if c['COLLECTION_AUTHORIZED'] == 'NO']

    itens = classificado.get('ITEMS') or []
    runs, custo, coletadas = [], 0.0, set()
    for p in PLATAFORMAS:
        d = _ler('POSTS-%s.json' % p)
        if not d:
            continue
        runs.extend(d.get('RUNS') or [])
        custo += d.get('COST_USD') or 0
        coletadas.add(p)

    pronto = 'READY' if itens else 'NOT_READY'
    return {
        'SOURCE_ID': 'COMPETITOR-PUBLIC-COMM/MEDICAO-PRIMEIRO-LOTE-V1',
        'DATASET_OWNER': DATASET_OWNER,
        'source': 'derivado dos artefatos desta missão — nenhuma execução',
        'SOURCE_LOCATION': 'derivado',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'MISSION_CLASS': 'AUXILIARY_NON_BLOCKING',
        'OPTIONAL_REFRESH_INPUT': pronto,
        'OPTIONAL_REFRESH_INPUT_WHY': (
            'há item coletado e classificado' if itens else
            'nenhum item coletado ainda. Identidade resolvida é insumo de COLETA, não '
            'de inteligência — e por isso não promove o handoff.'),
        'O_REFRESH_NAO_ESPERA_ISTO': [
            'EARLY SIGNAL TERRITORIAL', 'META COMPETITOR', 'COMPETITOR FORESIGHT'],

        'A_ACCOUNTS_ATTEMPTED': contas.get('ACCOUNTS_ATTEMPTED', 0),
        'B_ACCOUNTS_PROVED': len(provadas),
        'B_ACCOUNTS_AUTHORIZED_LOCAL': len(autorizadas),
        'C_REJECTED_NOT_AN_ACCOUNT': len(rejeitadas),
        'C_PROVED_BUT_NOT_ELIGIBLE': len(oficiais_fora),
        'C_EXCLUDED_BY_PRIMARY_REASON': (contas.get('EXCLUDED_BY_PRIMARY_REASON') or {}),
        'D_PLATFORMS_WITH_AUTHORIZED_ACCOUNT': sorted({c['PLATFORM'] for c in autorizadas}),
        'IDENTITY_STAGE': 'FREEZE_READY',
        'MANIFEST_STAGE': 'FREEZE_READY',
        'CONTENT_COLLECTION_STAGE': 'NOT_STARTED',
        'MISSION_STATE': 'READY_TO_COLLECT_WHEN_RUNNER_AVAILABLE',
        # AUSÊNCIA DE VALIDADOR NÃO É APROVAÇÃO. Escrever PASS aqui sem instrumento
        # seria a mesma classe de erro que esta missão persegue nos dados: um estado
        # confortável ocupando o lugar de "não medi".
        'WORKFLOW_STATIC_VALIDATION': 'NOT_MEASURED',
        'WORKFLOW_STATIC_VALIDATION_TRIED': [
            'gh api repos/:owner/:repo/actions/workflows — o workflow NÃO aparece, '
            'porque o GitHub só registra workflow que está no branch default, e este '
            'está num branch de missão. Sem registro, não há parse do lado deles.',
            'py -c import yaml — PyYAML não instalado',
            'node -e require("yaml") — módulo ausente; nenhum node_modules no repo',
            'ruby -ryaml, yamllint, actionlint — nenhum existe nesta máquina',
        ],
        'WORKFLOW_STATIC_VALIDATION_WHY_NOT': (
            'instalar dependência não estava autorizado nesta rodada, e um validador '
            'caseiro escrito por mim provaria a minha própria leitura do arquivo, não '
            'a do GitHub.'),
        'WORKFLOW_RUNTIME_VALIDATION': 'NOT_EXECUTED',
        'D_PLATFORMS_COLLECTED': sorted(coletadas),
        'E_TOTAL_ITEMS': len(itens),
        'F_WINDOW': ('%s dias' % (classificado.get('COLLECTION_WINDOW_DAYS') or NAO_SEI)
                     if itens else NAO_SEI),
        'G_ITEMS_BY_COMPETITOR': _conta('COMPANY', itens),
        'G_AUTHORIZED_BY_COMPETITOR': _conta('COMPANY', autorizadas),
        'G_AUTHORIZED_BY_COUNTRY': _conta('COUNTRY', autorizadas),
        'H_PRODUCT_COMMUNICATION': (classificado.get('BY_COMMUNICATION_TYPE') or {}
                                    ).get('PRODUCT_COMMUNICATION', 0),
        'I_TECHNICAL_COMMUNICATION': (classificado.get('BY_COMMUNICATION_TYPE') or {}
                                      ).get('TECHNICAL_EDUCATION', 0),
        'J_BY_CROP': classificado.get('BY_CROP') or {},
        'J_BY_ISSUE': classificado.get('BY_ISSUE') or {},
        'K_CREATOR_CROSSOVERS': 0,
        'K_CREATOR_CROSSOVER_NOTE': (
            'o Creator Map está congelado e não foi reaberto. Zero aqui significa '
            'nenhuma publicação coletada mencionou creator conhecido — e como zero '
            'publicações foram coletadas, este zero não mede nada sobre o mundo.'
            if not itens else
            'aparição observada nunca vira PAID_CREATOR_RELATION'),
        'L_READY_FOR_META_JOIN': 'NO' if not itens else 'YES',
        'L_META_NOTE': ('ORGANIC e PAID são camadas separadas. PUBLIC_COMMUNICATION=YES '
                        'com META_PAID_ACTIVITY=NO_OBSERVED é um estado válido, não uma '
                        'contradição.'),
        'M_READY_FOR_FORESIGHT_JOIN': 'NO' if not itens else 'YES',
        'M_FORESIGHT_NOTE': ('IP, BRAND, REGULATORY e PRODUCT continuam do Foresight. '
                             'Esta camada só entrega PUBLIC COMMUNICATION EVENTS e usa '
                             'ID de lá quando existir; senão, NOT_KNOWN.'),
        'N_COUNTRY_CROP_ISSUE_READINESS': (
            classificado.get('BY_COUNTRY_OF_FACT') or {}),
        'O_TOP_EVIDENCE': [i.get('URL') for i in itens[:10]],
        'P_RAW_PRESERVED': 'YES' if runs else 'n/a — nada foi coletado',
        'Q_APIFY_RUNS': len(runs),
        'Q_ITEMS': len(itens),
        'Q_COST_USD': round(custo, 6),

        'AS_QUATRO_AUSENCIAS': {
            'NOT_ATTEMPTED': universo.get('OUT_OF_FIRST_BATCH') or [],
            'NO_LINK_DECLARED': len(contas.get('NO_LINK_DECLARED') or []),
            'NOT_ELIGIBLE': len(oficiais_fora),
            'COLLECTED_ZERO': 0 if not itens else NAO_SEI,
        },
        'AS_QUATRO_AUSENCIAS_LEITURA': (
            'só COLLECTED_ZERO fala da EMPRESA. As outras três falam da NOSSA cobertura.'),
    }


if __name__ == '__main__':
    m = montar()
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'MEDICAO-PRIMEIRO-LOTE-V1.json'), 'w',
              encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=1)

    print('FUNIL DO PRIMEIRO LOTE')
    print('  casas tentadas .................. %d' % m['A_ACCOUNTS_ATTEMPTED'])
    print('  contas oficiais provadas ........ %d' % m['B_ACCOUNTS_PROVED'])
    print('  destas, LOCAIS e autorizadas .... %d' % m['B_ACCOUNTS_AUTHORIZED_LOCAL'])
    print('  oficiais fora do lote ........... %d  %s'
          % (m['C_PROVED_BUT_NOT_ELIGIBLE'], m['C_EXCLUDED_BY_PRIMARY_REASON']))
    print('  URLs que nem eram conta ......... %d' % m['C_REJECTED_NOT_AN_ACCOUNT'])
    print('  itens coletados ................. %d' % m['E_TOTAL_ITEMS'])
    print('  execucoes pagas / custo ......... %d / %.6f USD'
          % (m['Q_APIFY_RUNS'], m['Q_COST_USD']))
    print('')
    print('  autorizadas por empresa: %s' % m['G_AUTHORIZED_BY_COMPETITOR'])
    print('  autorizadas por pais:    %s' % m['G_AUTHORIZED_BY_COUNTRY'])
    print('  plataformas com conta:   %s' % m['D_PLATFORMS_WITH_AUTHORIZED_ACCOUNT'])
    print('')
    print('OPTIONAL_REFRESH_INPUT = %s' % m['OPTIONAL_REFRESH_INPUT'])
    print('  %s' % m['OPTIONAL_REFRESH_INPUT_WHY'])
