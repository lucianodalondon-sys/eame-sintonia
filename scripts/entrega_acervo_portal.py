#!/usr/bin/env python3
"""ACERVO_TO_PORTAL_DELIVERY_READY — a ponta de ENTREGA, não a fundação da coleta.

    python3 scripts/entrega_acervo_portal.py
    python3 scripts/entrega_acervo_portal.py --build
    python3 scripts/entrega_acervo_portal.py --json

ESTE ARQUIVO FOI RECLASSIFICADO, E O MOTIVO FICA ESCRITO
---------------------------------------------------------
Ele nasceu chamando-se `scripts/fundacao_coleta.py` e publicando
`COLLECTION_FOUNDATION_CLOSED`. Media bem e estava com o nome errado — o erro
mais caro deste repositório, porque não aparece como número errado:

    O ERRO NÃO FOI DE MEDIÇÃO. FOI DE NOME.

Já aconteceu aqui uma vez, quando `EAME_COLLECTION_ENTRY_GATE` fazia dois
trabalhos e foi declarado READY ao lado de `LOCATION_CONTRACT_COMPLETE = NO`.
A correção foi a mesma: separar os dois portões.

AS DUAS COISAS QUE ESTAVAM COLADAS
-----------------------------------
    A FUNDAÇÃO DA COLETA          termina em ADMISSION / READY:
        SOURCE → DISCOVER → FETCH → RAW → DERIVED → STRUCTURED
              → ADMISSION → READY
        Depois dela vem INTELIGÊNCIA. Só depois vem PORTAL.

    A ENTREGA ATÉ O PORTAL        é a ponta de baixo da cadeia, e é o que
        ESTE arquivo mede: ACERVO → PACOTE → ARTEFATO QUE A TELA CARREGA.

E a lei que a mistura violava:

    COLLECTION_FOUNDATION_CLOSED NÃO PODE DEPENDER DE PORTAL, PACOTE, TELA,
    UI NEM PRODUTO DE INTELIGÊNCIA.

Se dependesse, um portal incompleto impediria a coleta de fechar — invertendo a
ordem que o projeto exige de propósito: coleta antes de inteligência, e
inteligência antes de portal. Este portão fica **a jusante** dos três.

QUEM É O DONO CANÔNICO DE COLLECTION_FOUNDATION_CLOSED
-------------------------------------------------------
Não é este arquivo, e a busca foi feita antes da correção — por semântica, não
por nome. O dono é, na linha canônica `claude/collection-foundation-integration-v1`:

    leis/fundacao_da_coleta.py                          a constante e a trava
    docs/operacao/MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md   os critérios
    system-map/data/estradas-it.generated.json          o estado GERADO
    tests/test_fundacao_da_coleta.py                    as provas

    UMA PERGUNTA, UM DONO CANÔNICO.

Este arquivo **lê** esse estado quando ele estiver presente, e nunca o escreve,
nunca o deriva e nunca o contradiz. Enquanto as duas linhas estiverem separadas,
ele o reporta como `NAO_DISPONIVEL_NESTA_BRANCH` — que é diferente de NÃO, e
diferente de SIM.

O QUE ESTE PORTÃO RESPONDE, E O QUE ELE NÃO PODE RESPONDER
-----------------------------------------------------------
    RESPONDE       o que o acervo produz chega até o artefato que a tela carrega?
    NÃO RESPONDE   a coleta pode abrir? (dono acima)
                   a inteligência pode ser implementada? (dono acima)
                   a tela está completa? (outra pergunta ainda)

E o seu resultado NÃO é entrada de nenhuma dessas três. Uma fronteira de entrega
aberta **não** move o fechamento da coleta — há teste que reprova quem os
acoplar de novo.

CLASSE DESTE MEDIDOR
---------------------
    DELIVERY / LINEAGE / OBSERVABILITY

É um **precursor de sensor** da futura camada transversal de observabilidade de
fluxo, que a linha canônica instala depois da M1 e antes da M2. Não é uma
segunda plataforma de observabilidade e não deve virar uma: quando a camada
existir, este medidor vira um dos seus sensores, nas lentes ARCHITECTURE,
DIAGNOSTIC, TRACE e PERFORMANCE.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import portoes_eame as PORTOES                                    # noqa: E402

# A data da missão, fixa. Um artefato derivado sai byte-idêntico quando as
# entradas não mudam, e um carimbo de relógio faria cada regeração parecer
# fato novo.
DATA_DA_MISSAO = '2026-09-08'

SAIDA = os.path.join(RAIZ, 'data', 'samples', 'ENTREGA-ACERVO-PORTAL.json')
FRONTEIRA = os.path.join(RAIZ, 'data', 'samples', 'FRONTEIRA-ACERVO-PACOTE.json')
MEDIDOR_DA_FRONTEIRA = os.path.join(
    RAIZ, 'italia-portale', 'audit', 'fronteira-acervo-pacote.mjs')

# ── O DONO CANÔNICO DA OUTRA PERGUNTA ─────────────────────────────────
# Escrito aqui para que ninguém precise procurar de novo, e para que este
# arquivo nunca volte a se apresentar como dono.
DONO_CANONICO_DA_FUNDACAO_DA_COLETA = {
    'PERGUNTA': 'a fundação da coleta fechou?',
    'CONSTANTE': 'COLLECTION_FOUNDATION_CLOSED',
    'LINHA': 'claude/collection-foundation-integration-v1',
    'ARQUIVOS': ('leis/fundacao_da_coleta.py',
                 'docs/operacao/MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md',
                 'system-map/data/estradas-it.generated.json',
                 'tests/test_fundacao_da_coleta.py'),
    'ONDE_A_COLETA_TERMINA': 'ADMISSION / READY',
    'NAO_DEPENDE_DE': ('PORTAL', 'PACOTE', 'TELA', 'UI', 'PRODUTO_DE_INTELIGENCIA'),
    'ESTE_ARQUIVO_E_DONO': 'NAO',
}

# ── OS PILARES DESTE PORTÃO ───────────────────────────────────────────
# Um só, e de propósito. A versão anterior tinha três — ENTRADA, PRESERVAÇÃO e
# TRAVESSIA — e as duas primeiras são da fundação da coleta, não da entrega.
# Mantê-las aqui era o acoplamento que a correção desfez.
#
#     UM PORTÃO DE ENTREGA QUE EXIGE O PORTÃO DA COLETA
#     É O PORTÃO DA COLETA COM OUTRO NOME.
PILARES = {
    'TRAVESSIA': {
        'PERGUNTA': 'o que o acervo produz chega ao artefato que a tela carrega?',
        'MEDIDOR': 'italia-portale/audit/fronteira-acervo-pacote.mjs',
        'DERIVA_DE': 'FRONTEIRA_ATRAVESSADA',
        'PORQUE_E_PILAR':
            'é a única pergunta deste portão. A cadeia ACERVO → PACOTE → '
            'ARTEFATO é medível daqui de um lado, e é onde o CHECKPOINT desta '
            'linhagem localizou a perda principal da entrega.',
    },
}

# ── O QUE FICA A MONTANTE, E QUE ESTE PORTÃO NÃO AVALIA ────────────────
# Reportado como CONTEXTO para que a direção da cadeia fique visível — e
# marcado como não-pilar para que nunca volte a entrar no veredito.
CONTEXTO_A_MONTANTE = {
    'ENTRADA_DA_COLETA': {
        'DERIVA_DE': 'EAME_COLLECTION_ENTRY_GATE',
        'MEDIDOR': 'scripts/portoes_eame.py',
        'E_PILAR_DESTE_PORTAO': 'NAO',
        'PORQUE_NAO':
            'pertence à fundação da coleta, que termina em ADMISSION/READY e '
            'não passa pelo portal.',
    },
    'PRESERVACAO_DO_BRUTO': {
        'DERIVA_DE': 'RAW_PRESERVATION_GATE + RAW_CONTENT_INTEGRITY_GATE',
        'MEDIDOR': 'scripts/portoes_eame.py',
        'E_PILAR_DESTE_PORTAO': 'NAO',
        'PORQUE_NAO': 'idem — é degrau da coleta, a montante da entrega.',
    },
}


def _fronteira():
    if not os.path.exists(FRONTEIRA):
        return None, ('o artefato da fronteira não existe. Rode: node %s --build'
                      % os.path.relpath(MEDIDOR_DA_FRONTEIRA, RAIZ))
    with open(FRONTEIRA, encoding='utf-8') as h:
        return json.load(h), None


def _confere_a_safra(d):
    """NÃO MEDIDO DAQUI é resposta. Silêncio não é.

    Um artefato gravado contra um BUILD_ID que já não é o do portal mede outra
    safra — não é medição desatualizada, é medição de outra coisa.
    """
    try:
        r = subprocess.run(['node', MEDIDOR_DA_FRONTEIRA, '--json'],
                           capture_output=True, text=True, timeout=300, cwd=RAIZ)
    except (OSError, subprocess.SubprocessError) as e:
        return {'CONFERIDA': 'NAO', 'PORQUE': 'medidor não executável aqui: %s' % e}
    if r.returncode != 0:
        return {'CONFERIDA': 'NAO',
                'PORQUE': 'o medidor falhou: %s' % r.stderr.strip()[:200]}
    vivo = json.loads(r.stdout)
    igual = (vivo.get('BUILD_ID') == d.get('BUILD_ID')
             and vivo.get('FRONTEIRA_ATRAVESSADA') == d.get('FRONTEIRA_ATRAVESSADA')
             and vivo.get('FAMILIAS_ABERTAS') == d.get('FAMILIAS_ABERTAS'))
    return {
        'CONFERIDA': 'SIM' if igual else 'NAO',
        'BUILD_ID_NO_ARTEFATO': d.get('BUILD_ID'),
        'BUILD_ID_MEDIDO_AGORA': vivo.get('BUILD_ID'),
        'PORQUE': None if igual else
            'o artefato no disco não reproduz o que o medidor mede agora — '
            'regrave com --build antes de ler este portão',
    }


def _estado_da_fundacao_da_coleta():
    """LER o dono canônico quando ele estiver presente. Nunca derivá-lo.

    As duas linhas estão separadas nesta missão, por instrução: nada é mergeado
    daqui. Enquanto o arquivo do dono não estiver nesta árvore, a resposta é
    NAO_DISPONIVEL_NESTA_BRANCH — que não é NÃO e não é SIM.

        LER O DONO NÃO É SER O DONO.
        E NÃO TER O DONO À MÃO NÃO AUTORIZA RESPONDER POR ELE.
    """
    caminho = os.path.join(RAIZ, 'leis', 'fundacao_da_coleta.py')
    if not os.path.exists(caminho):
        return {
            'VALOR': 'NAO_DISPONIVEL_NESTA_BRANCH',
            'PORQUE': 'o dono canônico vive em %s e não foi mergeado nesta '
                      'missão, por instrução.'
                      % DONO_CANONICO_DA_FUNDACAO_DA_COLETA['LINHA'],
            'LIDO_DE': None,
        }
    sys.path.insert(0, os.path.join(RAIZ, 'leis'))
    import fundacao_da_coleta as DONO                              # noqa: E402
    return {
        'VALOR': 'SIM' if DONO.COLLECTION_FOUNDATION_CLOSED else 'NAO',
        'PORQUE': 'lido do dono canônico, sem redefinir nada.',
        'LIDO_DE': 'leis/fundacao_da_coleta.py',
    }


def avalia():
    p = PORTOES.monta()
    fronteira, faltou = _fronteira()

    pilares = {}
    if fronteira is None:
        pilares['TRAVESSIA'] = dict(PILARES['TRAVESSIA'], **{
            'ESTADO': 'NAO_MEDIDO', 'MEDIDO': 'NAO',
            'EVIDENCIA': faltou, 'BLOQUEADORES': ['FRONTEIRA_NAO_MEDIDA'],
        })
    else:
        safra = _confere_a_safra(fronteira)
        atravessa = fronteira['FRONTEIRA_ATRAVESSADA'] == 'SIM'
        if safra['CONFERIDA'] != 'SIM':
            estado = 'NAO_MEDIDO'
        else:
            estado = 'FECHADO' if atravessa else 'ABERTO'
        pilares['TRAVESSIA'] = dict(PILARES['TRAVESSIA'], **{
            'ESTADO': estado,
            'MEDIDO': 'SIM' if safra['CONFERIDA'] == 'SIM' else 'NAO',
            'EVIDENCIA': 'BUILD %s · %d de %d famílias abertas' % (
                fronteira['BUILD_ID'], len(fronteira['FAMILIAS_ABERTAS']),
                len(fronteira['FAMILIAS'])),
            'BLOQUEADORES': fronteira['FAMILIAS_ABERTAS'],
            'SAFRA': safra,
            'DONO': fronteira['DONO_DA_FRONTEIRA'],
            'ACOES_MINIMAS': [
                {'FAMILIA': f['FAMILIA'], 'ACAO': f['ACAO_MINIMA'],
                 'DONO': f['DONO_DA_ACAO'], 'ESTADO': f['ESTADO']}
                for f in fronteira['FAMILIAS']
                if not f['ESTADO'].startswith('FECHADA')],
            'DEGRAUS_ABERTOS': fronteira.get('DEGRAUS_ABERTOS', []),
        })

    # o contexto a montante, LIDO e nunca somado ao veredito
    entrada = p['PORTOES']['EAME_COLLECTION_ENTRY_GATE']
    raw = p.get('RAW_PRESERVATION_GATE', {})
    contexto = {
        'ENTRADA_DA_COLETA': dict(CONTEXTO_A_MONTANTE['ENTRADA_DA_COLETA'],
                                  ESTADO_LIDO=entrada['ESTADO']),
        'PRESERVACAO_DO_BRUTO': dict(CONTEXTO_A_MONTANTE['PRESERVACAO_DO_BRUTO'],
                                     ESTADO_LIDO='%s / %s' % (
                                         raw.get('ESTADO'),
                                         raw.get('RAW_CONTENT_INTEGRITY_GATE'))),
        'FUNDACAO_DA_COLETA': dict(DONO_CANONICO_DA_FUNDACAO_DA_COLETA,
                                   ESTADO_LIDO=_estado_da_fundacao_da_coleta()),
    }

    abertos = [n for n, v in pilares.items() if v['ESTADO'] != 'FECHADO']
    pronto = not abertos

    return {
        'SOURCE_ID': 'ENTREGA-ACERVO-PORTAL',
        'VERSION': 2,
        'captured_at': DATA_DA_MISSAO,
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt',
        'DERIVADO_DE': ['italia-portale/audit/fronteira-acervo-pacote.mjs',
                        'data/samples/FRONTEIRA-ACERVO-PACOTE.json'],
        'CLASSE': 'DELIVERY / LINEAGE / OBSERVABILITY',
        'PRECURSOR_DE':
            'a camada transversal de observabilidade de fluxo, instalada pela '
            'linha canônica depois da M1 e antes da M2. Este medidor será um '
            'sensor dela, não uma segunda plataforma.',
        'O_QUE_ISTO_E':
            'a prontidão da ENTREGA: o que o acervo produz chega ao artefato '
            'que a tela carrega? Derivado de medidor executável.',
        'O_QUE_ISTO_NAO_E':
            'não é a fundação da coleta, não a fecha, não a abre e não entra '
            'no cálculo dela. A coleta termina em ADMISSION/READY e não passa '
            'pelo portal.',
        'PERGUNTA': PILARES['TRAVESSIA']['PERGUNTA'],
        'PILARES': pilares,
        'ACERVO_TO_PORTAL_DELIVERY_READY': 'SIM' if pronto else 'NAO',
        'PILARES_ABERTOS': abertos,
        'O_QUE_FALTA_PARA_SIM': [
            {'PILAR': n, 'ESTADO': pilares[n]['ESTADO'],
             'BLOQUEADORES': pilares[n]['BLOQUEADORES'],
             'DONO': pilares[n].get('DONO', 'esta linhagem')}
            for n in abertos],
        'CONTEXTO_A_MONTANTE': contexto,
        'REGRA': 'UMA PERGUNTA, UM DONO CANÔNICO. E NÃO MEDIDO NÃO É FECHADO.',
        'O_QUE_UM_NAO_AQUI_NAO_SIGNIFICA':
            'NÃO significa que a coleta não pode fechar. A ordem do projeto é '
            'coleta → inteligência → portal, e este portão é o último dos três: '
            'ele pode ficar aberto por muito tempo sem que isso diga nada sobre '
            'os dois anteriores.',
    }


def monta():
    return avalia()


def _imprime(d):
    print('')
    print('  A ENTREGA ACERVO → PORTAL   [%s]' % d['CLASSE'])
    print('  ' + '-' * 74)
    for nome, p in d['PILARES'].items():
        print('  %-14s %-12s %s' % (nome, p['ESTADO'], p['EVIDENCIA']))
        for b in p['BLOQUEADORES']:
            print('  %-14s %-12s   bloqueia: %s' % ('', '', b))
    print('  ' + '-' * 74)
    print('  ACERVO_TO_PORTAL_DELIVERY_READY = %s'
          % d['ACERVO_TO_PORTAL_DELIVERY_READY'])
    print('')
    print('  A MONTANTE, e NÃO avaliado por este portão:')
    for nome, c in d['CONTEXTO_A_MONTANTE'].items():
        v = c['ESTADO_LIDO']
        v = v['VALOR'] if isinstance(v, dict) else v
        print('    %-22s %s' % (nome, v))
    print('')
    print('  COLLECTION_FOUNDATION_CLOSED tem dono canônico em %s'
          % DONO_CANONICO_DA_FUNDACAO_DA_COLETA['LINHA'])
    print('  e a coleta termina em %s — não no portal.'
          % DONO_CANONICO_DA_FUNDACAO_DA_COLETA['ONDE_A_COLETA_TERMINA'])
    print('')


if __name__ == '__main__':
    d = monta()
    if '--json' in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    elif '--build' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8') as h:
            json.dump(d, h, ensure_ascii=False, indent=2)
            h.write('\n')
        print('gravado: %s' % os.path.relpath(SAIDA, RAIZ))
    else:
        _imprime(d)
