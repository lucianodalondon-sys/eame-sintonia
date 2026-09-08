#!/usr/bin/env python3
"""CENSO DA OBSERVABILIDADE — o que ja se consegue perguntar, e o que nao.

    python3 system-map/scripts/censo_da_observabilidade.py

    NUNCA VERDE POR SILENCIO.

Uma dimensao sem dado nao e uma dimensao saudavel. Este censo separa tres
respostas que um mapa mal feito juntaria numa cor so:

    NOT_INSTRUMENTED   ninguem emite. Nao ha o que medir
    NOT_MEASURED       emite-se, e ninguem foi ler
    MEDIDO             ha dado, e ele esta aqui

⚠️ A DIFERENCA IMPORTA porque as tres pedem coisas diferentes: a primeira pede
codigo que emita, a segunda pede um leitor, a terceira pede leitura.

O QUE ELE FORMALIZA
-------------------
Dois estados que ate agora existiam so em prosa:

    OBSERVABILITY_READY   uma rota nova tem CONTRATO para emitir telemetria
                          e ser diagnosticada?
    EVOLUTION_READY       uma decisao pode ter versao, baseline, e outcome
                          ligado?

⚠️ NENHUM DOS DOIS SIGNIFICA «PRONTO PARA USAR». `OBSERVABILITY_READY` nao quer
dizer que se esta a medir — quer dizer que quem quiser medir tem contrato onde
se apoiar. E `EVOLUTION_READY` nao quer dizer IA autonoma pronta: quer dizer
que uma experiencia teria onde ser guardada.

    CONTRATO PRONTO != INSTRUMENTADO != OBSERVADO.

E COLLECTION_FOUNDATION_CLOSED CONTINUA NAO
-------------------------------------------
O scanner existir nao fecha fundacao nenhuma. Sao perguntas diferentes, e este
censo nao toca na primeira: le-a do dono.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import telemetria as tel            # noqa: E402
import evolucao as evo              # noqa: E402
import gestao_da_coleta as ges      # noqa: E402
import aprender_com_a_fonte as apr  # noqa: E402
import fundacao_da_coleta as fdc    # noqa: E402

FLUXO = os.path.join(RAIZ, 'system-map', 'data', 'fluxo.generated.json')
DONOS = os.path.join(RAIZ, 'system-map', 'data', 'donos.generated.json')
SAIDA = os.path.join(RAIZ, 'system-map', 'data',
                     'observabilidade.generated.json')


def _ler(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def dimensoes(fluxo):
    """Cada dimensao do mapa, com a resposta HONESTA de tres valores."""
    tem_corridas = bool(fluxo and fluxo.get('CORRIDAS'))
    d = []

    d.append({
        'DIMENSAO': 'ARCHITECTURE',
        'ESTADO': 'MEDIDO',
        'ONDE': 'system-map/data/estradas-it.generated.json',
        'O_QUE_RESPONDE': 'que etapas existem, quem e dono, e quem esta ligado',
    })
    d.append({
        'DIMENSAO': 'TRACE',
        'ESTADO': 'MEDIDO' if tem_corridas else 'NOT_INSTRUMENTED',
        'ONDE': 'system-map/data/fluxo.generated.json',
        'O_QUE_RESPONDE': 'que corridas houve, e o que entrou e saiu de cada',
        'RESSALVA': ('so a RC-9 emite. As outras rotas nao emitiram ZERO — '
                     'nao emitem NADA.'),
    })
    d.append({
        'DIMENSAO': 'DIAGNOSTIC',
        'ESTADO': 'NOT_INSTRUMENTED',
        'ONDE': None,
        'O_QUE_RESPONDE': 'em que codigo cada etapa parou',
        'PORQUE': ('o contrato tem %d codigos declarados, e nenhum executor os '
                   'emite ainda. Quem teria de emitir: cada executor.'
                   % len(tel.CODIGOS_DE_DIAGNOSTICO)),
    })
    d.append({
        'DIMENSAO': 'PERFORMANCE',
        'ESTADO': 'PARCIAL' if tem_corridas else 'NOT_INSTRUMENTED',
        'ONDE': 'system-map/data/fluxo.generated.json',
        'O_QUE_RESPONDE': 'quanto tempo e quanto custou',
        'RESSALVA': ('ha duracao POR CORRIDA e nao por etapa. Custo: '
                     'NOT_INSTRUMENTED — nenhuma rota italiana e paga hoje.'),
    })
    d.append({
        'DIMENSAO': 'EVOLUTION',
        'ESTADO': 'NOT_MEASURED',
        'ONDE': 'leis/evolucao.py',
        'O_QUE_RESPONDE': 'que alternativas foram comparadas e o que se decidiu',
        'PORQUE': ('ha contrato e nao ha experiencia nenhuma registada. '
                   'NOT_MEASURED e nao NOT_INSTRUMENTED: o sitio existe, o '
                   'dado e que nao.'),
    })
    d.append({
        'DIMENSAO': 'COLLECTION_STRATEGY',
        'ESTADO': 'NOT_MEASURED',
        'ONDE': 'leis/gestao_da_coleta.py',
        'O_QUE_RESPONDE': 'que faltas se conhecem, e o que se decidiu sobre elas',
        'PORQUE': 'ha contrato e nenhuma necessidade declarada ainda.',
    })
    return d


def observability_ready(donos):
    """UMA ROTA NOVA TEM ONDE SE APOIAR PARA EMITIR E SER DIAGNOSTICADA?

    ⚠️ Isto NAO diz que se esta a medir. Diz que quem quiser medir tem contrato.
    """
    faltas = []
    if not tel.CODIGOS_DE_DIAGNOSTICO:
        faltas.append('sem codigos de diagnostico declarados')
    for campo in ('LAST_GOOD_STAGE', 'RESUME_SAFE', 'POLICY_VERSION'):
        if campo not in tel.CAMPOS_DO_RUN:
            faltas.append('o run nao declara %s' % campo)
    for campo in ('INPUT_GRAIN', 'OUTPUT_GRAIN', 'UNACCOUNTED_INPUT'):
        if campo not in tel.CAMPOS_DA_ETAPA:
            faltas.append('a etapa nao declara %s' % campo)
    if 'NOT_RUN' not in tel.ESTADOS_DE_ETAPA:
        faltas.append('nao ha como dizer NOT_RUN')
    return {
        'OBSERVABILITY_READY': 'SIM' if not faltas else 'NAO',
        'O_QUE_SIGNIFICA': ('uma rota nova tem CONTRATO para emitir telemetria '
                            'e ser diagnosticada. NAO significa que se esta a '
                            'medir.'),
        'O_QUE_NAO_SIGNIFICA': 'CONTRATO PRONTO != INSTRUMENTADO != OBSERVADO',
        'FALTAS': faltas,
        'QUANTOS_CONCEITOS_COM_DONO_DUPLICADO': sum(
            1 for c in (donos or {}).get('DETALHE', [])
            if c['ESTADO'] == 'DONO_DUPLICADO'),
        'PORQUE_O_DUPLICADO_IMPORTA': (
            'onde dois ficheiros escrevem o mesmo conceito, a telemetria pode '
            'divergir sem ninguem dar por isso. Nao impede o contrato de estar '
            'pronto; e a divida que vem a seguir.'),
    }


def evolution_ready():
    """UMA DECISAO PODE TER VERSAO, BASELINE E OUTCOME LIGADO?

    ⚠️ NAO significa IA autonoma pronta.
    """
    faltas = []
    if 'BASELINE' not in evo.PAPEIS:
        faltas.append('sem baseline nao ha com que comparar')
    if 'COMO_SE_DESFAZ' not in evo.CAMPOS_DA_PROMOCAO:
        faltas.append('promocao sem caminho de volta')
    if 'PROMOTION_ID' not in evo.CAMPOS_DO_ROLLBACK:
        faltas.append('rollback nao liga a promocao')
    if 'DECISION_ID' not in ges.CAMPOS_DO_RESULTADO:
        faltas.append('resultado nao liga a decisao')
    if 'POLICY_VERSION' not in ges.CAMPOS_DA_DECISAO:
        faltas.append('decisao sem versao de politica')
    return {
        'EVOLUTION_READY': 'SIM' if not faltas else 'NAO',
        'O_QUE_SIGNIFICA': ('decisoes tem versao, ha baseline, e outcome pode '
                            'ser ligado a decisao. Uma experiencia teria onde '
                            'ser guardada.'),
        'O_QUE_NAO_SIGNIFICA': 'NAO significa IA autonoma pronta',
        'FALTAS': faltas,
        'PROIBIDO_HOJE': list(evo.PROIBIDO_HOJE),
    }


def main():
    fluxo = _ler(FLUXO)
    donos = _ler(DONOS)
    dims = dimensoes(fluxo)
    obs = observability_ready(donos)
    evl = evolution_ready()

    rel = {
        'SCHEMA': 'observabilidade/v1',
        'NUNCA_VERDE_POR_SILENCIO': (
            'uma dimensao sem dado nao e uma dimensao saudavel. '
            'NOT_INSTRUMENTED (ninguem emite) != NOT_MEASURED (emite-se e '
            'ninguem leu) != MEDIDO. As tres pedem coisas diferentes.'),
        'DIMENSOES': dims,
        'POR_ESTADO': {e: sum(1 for d in dims if d['ESTADO'] == e)
                       for e in sorted({d['ESTADO'] for d in dims})},
        'OBSERVABILITY': obs,
        'EVOLUTION': evl,
        'COLLECTION_FOUNDATION_CLOSED': fdc.COLLECTION_FOUNDATION_CLOSED,
        'O_SCANNER_EXISTIR_NAO_FECHA_FUNDACAO': (
            'sao perguntas diferentes. Este censo nao decide a fundacao: '
            'le-a de leis/fundacao_da_coleta.py, que e o dono.'),
        'CONTRATOS_QUE_JA_EXISTEM': {
            'TELEMETRIA': tel.CONTRATO,
            'GESTAO_DA_COLETA': ges.CONTRATO,
            'APRENDER_COM_A_FONTE': apr.CONTRATO,
            'EVOLUCAO': evo.CONTRATO,
        },
    }
    with open(SAIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
        f.write('\n')

    print('DIMENSOES %s' % rel['POR_ESTADO'])
    for d in dims:
        print('  %-20s %-18s %s' % (d['DIMENSAO'], d['ESTADO'],
                                    d.get('ONDE') or ''))
    print('')
    print('OBSERVABILITY_READY = %s   (contrato pronto != instrumentado)'
          % obs['OBSERVABILITY_READY'])
    print('EVOLUTION_READY     = %s   (nao significa IA autonoma pronta)'
          % evl['EVOLUTION_READY'])
    print('COLLECTION_FOUNDATION_CLOSED = %s'
          % ('SIM' if rel['COLLECTION_FOUNDATION_CLOSED'] else 'NAO'))
    print('\nescrito em %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
