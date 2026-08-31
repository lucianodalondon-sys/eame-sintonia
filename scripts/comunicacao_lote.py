#!/usr/bin/env python3
"""
LOTE CONGELADO DA PRIMEIRA COLETA — a lista que a execução real vai obedecer.

    py scripts/comunicacao_lote.py

POR QUE UM ARQUIVO SÓ PARA A LISTA
-----------------------------------
`CONTAS-V1.json` é o resultado de uma RÉGUA: ele muda quando a régua muda, e isso é bom
enquanto ninguém gastou dinheiro. A partir do momento em que a coleta paga roda, a lista
precisa parar de se mexer — senão fica impossível dizer contra o quê o rendimento foi
medido. Este arquivo é a fotografia: congelada, datada, e só substituída por uma V2
explícita.

    LISTA QUE MUDA SOZINHA APAGA A MEDIÇÃO DO RENDIMENTO.

QUEM ENTRA
-----------
As TRÊS perguntas têm que fechar: `ACCOUNT_IDENTITY_STATE = PROVED`, `COUNTRY_SCOPE =
LOCAL_COUNTRY_PROVED` e `PAGE_ROLE = COMPANY`.

Ficam de fora, e ficam ESCRITOS no próprio manifesto para que a ausência seja legível.
O motivo primário separa DOIS eixos que não podem virar um:

  · GLOBAL              eixo PAÍS. A conta é oficial e é do grupo (LinkedIn
                        /company/basf, /bayer-cropscience).
  · COUNTRY_NOT_KNOWN   eixo PAÍS. Não deu para fechar por rota pública — as três
                        contas de LinkedIn da Nufarm batem em muro de cadastro, e
                        entrar com login não é rota autorizada nesta casa. Limite da
                        NOSSA rota, não da empresa.
  · PRODUCT_BRAND_ROLE  eixo PAPEL, e NÃO é um estado de país. A `DEKALB France` tem o
                        país **PROVADO** — a página se chama assim e aponta para
                        bayer-agri.fr — e mesmo assim fica fora, porque é marca de
                        semente e o lote é COMPANY x COUNTRY. Chamá-la de "não local"
                        era falso, e essa era a redação anterior deste arquivo.

A ORDEM DE EXECUÇÃO É PARTE DO CONTRATO
-----------------------------------------
YouTube primeiro. Não é preferência: o YouTube devolve TÍTULO, DESCRIÇÃO e DATA em campo
próprio, e é onde a classificação do §5/§6 pode ser medida com menos ambiguidade antes de
abrir Instagram e Facebook, que dependem muito mais de legenda solta e de imagem — e a
imagem, por lei desta missão, não prova cultura nenhuma.

LinkedIn não tem passo aqui: das cinco empresas, NENHUMA tem conta local provada nessa
plataforma. Isso não é "as empresas não usam LinkedIn"; é "o site oficial local não
declarou conta local de LinkedIn, e a rota pública para conferir está fechada".
"""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'COMPETITOR-PUBLIC-COMM')
CONTAS = os.path.join(SAIDA, 'CONTAS-V1.json')
DATASET_OWNER = 'COMPETITOR_PUBLIC_COMMUNICATION_EAME'

# YouTube primeiro, e o motivo está no cabeçalho. Instagram e Facebook só se o
# rendimento do YouTube justificar; LinkedIn só quando houver conta local provada.
ORDEM = ['YOUTUBE', 'INSTAGRAM', 'FACEBOOK', 'LINKEDIN']


def montar(caminho=CONTAS):
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)

    dentro, fora = [], []
    for c in d['ACCOUNTS']:
        if c['ACCOUNT_IDENTITY_STATE'] != 'PROVED':
            continue
        linha = {
            'COUNTRY': c['COUNTRY'],
            'COMPANY': c['COMPANY'],
            'PLATFORM': c['PLATFORM'],
            'ACCOUNT_HANDLE': c['ACCOUNT_HANDLE'],
            'ACCOUNT_URL': c['ACCOUNT_URL'],
            'COUNTRY_SCOPE': c['COUNTRY_SCOPE'],
            'PAGE_ROLE': c['PAGE_ROLE'],
            'IDENTITY_EVIDENCE': c['ACCOUNT_IDENTITY_EVIDENCE'],
            'COUNTRY_SCOPE_EVIDENCE': c['COUNTRY_SCOPE_EVIDENCE'],
            'PAGE_ROLE_EVIDENCE': c['PAGE_ROLE_EVIDENCE'],
        }
        if c.get('COUNTRY_SCOPE_CHAIN'):
            linha['COUNTRY_SCOPE_CHAIN'] = c['COUNTRY_SCOPE_CHAIN']
        (dentro if c['COLLECTION_AUTHORIZED'] == 'YES' else fora).append(linha)

    dentro.sort(key=lambda x: (ORDEM.index(x['PLATFORM']), x['COUNTRY'], x['COMPANY']))

    passos, acumulado = [], 0
    for i, p in enumerate(ORDEM, 1):
        contas_p = [x for x in dentro if x['PLATFORM'] == p]
        acumulado += len(contas_p)
        passos.append({
            'STEP': 'ABCD'[i - 1],
            'PLATFORM': p,
            'ACCOUNTS': len(contas_p),
            'GATE': ('rodar `contratos` antes — GET no ator, custo zero'
                     if i == 1 else
                     'só se o rendimento do passo anterior justificar')
            if p != 'LINKEDIN' else
            'bloqueado: nenhuma conta local provada nesta plataforma',
        })

    por_pais, por_empresa, por_plataforma = {}, {}, {}
    for x in dentro:
        por_pais[x['COUNTRY']] = por_pais.get(x['COUNTRY'], 0) + 1
        por_empresa[x['COMPANY']] = por_empresa.get(x['COMPANY'], 0) + 1
        por_plataforma[x['PLATFORM']] = por_plataforma.get(x['PLATFORM'], 0) + 1

    fora_por_escopo = {}
    for x in fora:
        k = ('PRODUCT_BRAND_ROLE' if x['PAGE_ROLE'] != 'COMPANY'
             else ('COUNTRY_NOT_KNOWN' if x['COUNTRY_SCOPE'] == 'NOT_KNOWN'
                   else x['COUNTRY_SCOPE']))
        fora_por_escopo[k] = fora_por_escopo.get(k, 0) + 1

    return {
        'SOURCE_ID': 'PUBLIC-COMM-FIRST-BATCH-EAME',
        'DATASET_OWNER': DATASET_OWNER,
        'VERSION': 'V1',
        'FROZEN_AT': datetime.date.today().isoformat(),
        'FROZEN_RULE': (
            'esta lista NÃO muda depois da primeira coleta paga. Critério novo produz '
            'uma V2 explícita, com a V1 preservada — senão o rendimento fica medido '
            'contra um denominador que se mexeu.'),
        'ENTRY_RULE': ('ACCOUNT_IDENTITY_STATE = PROVED E COUNTRY_SCOPE = '
                       'LOCAL_COUNTRY_PROVED E PAGE_ROLE = COMPANY'),
        'source': 'derivado de CONTAS-V1 — nenhuma coleta, nenhum custo',
        'EVIDENCE_CLASS': 'DERIVED_SCOPE',
        'APIFY_RUNS': 0, 'COST_USD': 0,

        'ACCOUNTS_IN_BATCH': len(dentro),
        'BY_COUNTRY': por_pais,
        'BY_COMPANY': por_empresa,
        'BY_PLATFORM': por_plataforma,

        'EXECUTION_ORDER': passos,
        'WINDOW_FIRST': 'LAST_30D',
        'WINDOW_WIDEN_TO': 'LAST_90D',
        'WINDOW_WIDEN_RULE': 'só onde o corpus vier baixo. Nunca histórico profundo na '
                             'primeira execução.',

        'ACCOUNTS': dentro,

        'EXCLUDED_ACCOUNTS': fora,
        'EXCLUDED_BY_PRIMARY_REASON': fora_por_escopo,
        'EXCLUDED_MEANS': (
            'conta OFICIAL que não entra no lote COMPANY x COUNTRY. O motivo pode ser '
            'o PAÍS (global, ou não provado) OU o PAPEL (página de marca/produto). '
            'PRODUCT_BRAND_ROLE não quer dizer que o país seja desconhecido: a DEKALB '
            'France tem o país PROVADO e fica fora pelo papel. Nenhum destes casos é '
            'conta errada, e nenhum é empresa que não comunica.'),
        'IDENTITY_STAGE': 'FREEZE_READY',
        'MANIFEST_STAGE': 'FREEZE_READY',
        'CONTENT_COLLECTION_STAGE': 'NOT_STARTED',
        'MISSION_STATE': 'READY_TO_COLLECT_WHEN_RUNNER_AVAILABLE',
        'MISSION_IS_NOT_FINISHED_BECAUSE': (
            'falta conteúdo real. Identidade congelada não responde "sobre o que a '
            'empresa está falando" nem "o que mudou".'),

        'ZERO_MEANS_NOW': ('NO_CONTENT_COLLECTION_EXECUTED — nenhuma coleta rodou. '
                           'Nenhum zero desta missão fala sobre o mundo ainda.'),
        'ZERO_WILL_MEAN_AFTER_A_VALID_RUN': (
            'NO_ITEMS_OBSERVED nesta conta provada, nesta plataforma, nesta janela, '
            'nesta execução bem-sucedida. NUNCA COMPANY_NOT_COMMUNICATING.'),
        'OPTIONAL_REFRESH_INPUT': 'NOT_READY',
        'STATE': 'READY_TO_COLLECT_WHEN_RUNNER_AVAILABLE',
    }


if __name__ == '__main__':
    m = montar()
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, 'PUBLIC-COMM-FIRST-BATCH-EAME.json'), 'w',
              encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=1)

    print('LOTE CONGELADO EM %s · %d contas' % (m['FROZEN_AT'], m['ACCOUNTS_IN_BATCH']))
    print('  por pais:       %s' % m['BY_COUNTRY'])
    print('  por empresa:    %s' % m['BY_COMPANY'])
    print('  por plataforma: %s' % m['BY_PLATFORM'])
    print('')
    print('ORDEM DE EXECUCAO')
    for p in m['EXECUTION_ORDER']:
        print('  passo %s  %-10s %2d contas  · %s'
              % (p['STEP'], p['PLATFORM'], p['ACCOUNTS'], p['GATE']))
    print('')
    print('FORA DO LOTE (oficiais, por pais OU por papel): %d  %s'
          % (len(m['EXCLUDED_ACCOUNTS']), m['EXCLUDED_BY_PRIMARY_REASON']))
    print('ESTADO: %s' % m['STATE'])
