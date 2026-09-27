#!/usr/bin/env python3
"""O FLUXO NO SECO — provar que a telemetria distingue o que tem de distinguir.

    python3 provas/fluxo_no_seco.py

    MODULE WORKS != EDGE WORKS != FLOW WORKS.

O contrato em `leis/telemetria.py` diz que uma etapa a jusante de uma que
falhou NAO falhou — ela nunca comecou. Dizer isso e facil. Esta prova mostra a
diferenca a acontecer, num fluxo de mentira, e exige que o relato saia certo.

    UM CONTRATO QUE NUNCA FOI EXERCIDO
    E UMA INTENCAO, NAO UMA GARANTIA.

O QUE ELA NAO TOCA
------------------
Zero rede. Zero producao. Zero ficheiro do repositorio. Tudo acontece em
memoria, com uma fonte inventada. Ela mede o RELATO, nao o mundo.

O QUE ELA PROVA
---------------
    1. a etapa a montante passa
    2. a etapa do meio falha, com codigo de diagnostico
    3. as etapas a jusante ficam NOT_RUN — nao FAIL
    4. o retrato do momento da falha e guardado
    5. LAST_GOOD_STAGE aponta para a ultima que passou
    6. retomar continua de la, sem repetir o que ja estava feito
    7. a conta fecha: UNACCOUNTED_INPUT = 0, mesmo com a falha
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import telemetria as t  # noqa: E402
import diagnostico as dg  # noqa: E402
import falhas as falhas_lei  # noqa: E402

# O estado do ITEM, lido do dono — e nao escrito a mao aqui. Se `falhas.py`
# deixar de o declarar, esta prova rebenta em vez de mentir.
ESTADO_DO_ITEM = 'EXECUTOR_UNAVAILABLE'
assert ESTADO_DO_ITEM in falhas_lei.ESTADOS, (
    'leis/falhas.py deixou de declarar %s' % ESTADO_DO_ITEM)

# A cadeia que qualquer estrada percorre. A do meio vai falhar de proposito.
ETAPAS = ('DISCOVER', 'FETCH', 'RAW', 'DERIVED', 'STRUCTURED', 'ADMISSION')
ONDE_FALHA = 'RAW'


def _etapa(nome, estado, entrada=0, **kw):
    linha = {
        'RUN_ID': kw.get('run_id', 'DRY-RUN-1'),
        'STAGE': nome, 'STAGE_STATE': estado,
        'INPUT_GRAIN': kw.get('gi', 'documento'),
        'OUTPUT_GRAIN': kw.get('go', 'documento'),
        'INPUT_COUNT': entrada, 'OUTPUT_COUNT': kw.get('saida', 0),
        # ⚠️ `ERROR`, E NAO `ERRORS`. O balde chama-se `ERROR` no contrato —
        # `telemetria.DESTINOS_DO_ITEM` — e e assim que o runtime a serio o
        # escreve (`medidas/rastro_da_coleta.py:210`). Esta prova inventava o
        # plural, e por isso a propria reconciliacao dela nao fechava: o
        # `reconcilia()` somava um balde que nao existia e sobravam 4 itens.
        # Um sinonimo sem dono nao e um detalhe de escrita: e uma conta errada.
        'PASSED': kw.get('passou', 0), 'REJECTED': kw.get('rejeitado', 0),
        'ERROR': kw.get('erros', 0), 'NOT_RUN': kw.get('nao_correu', 0),
        'UNKNOWN': kw.get('desconhecido', 0), 'DEDUPED': kw.get('repetido', 0),
        'DIAGNOSTIC_CODE': kw.get('codigo'),
        # O estado canonico do ITEM, de `leis/falhas.py`. Campo separado de
        # proposito: a `024` tambem os separa (`diagnostic_code` e
        # `canonical_state`), porque respondem a perguntas diferentes.
        'CANONICAL_STATE': kw.get('estado_do_item'),
        'DURATION_MS': kw.get('ms', 0),
    }
    _fecha, sobra = t.reconcilia(linha)
    linha['UNACCOUNTED_INPUT'] = sobra if sobra is not None else None
    return linha


def corrida_que_falha_no_meio():
    """10 documentos entram. A etapa RAW nao tem a ferramenta na maquina."""
    etapas, ultima_boa, ja_falhou = [], None, False
    entrada = 10
    for nome in ETAPAS:
        if ja_falhou:
            # ⚠️ NOT_RUN, E NAO FAIL. Estas etapas nunca comecaram. Marca-las
            # como falhadas faria UM defeito parecer TRES.
            etapas.append(_etapa(nome, 'NOT_RUN', entrada,
                                 nao_correu=entrada,
                                 codigo='UPSTREAM_NOT_RUN'))
            continue
        if nome == ONDE_FALHA:
            # 6 passaram antes de a ferramenta faltar; 4 ficaram por processar.
            #
            # ⚠️ DUAS PERGUNTAS, DOIS NOMES — e esta prova punha um so.
            # Ela escrevia `EXECUTOR_UNAVAILABLE` no `DIAGNOSTIC_CODE`, e
            # `EXECUTOR_UNAVAILABLE` nao e um codigo de diagnostico: e um
            # ESTADO DE FALHA DO ITEM, de `leis/falhas.py:216` («a nossa
            # ferramenta nao esta la... Nada foi medido sobre a fonte»).
            #
            #     O ESTADO E DO ITEM. O DIAGNOSTICO E DA ETAPA.
            #
            # `provas/paridade_da_lingua.py:101` guarda essa fronteira e
            # recusa qualquer nome que sirva as duas perguntas. Ninguem
            # corria esta prova, e por isso a confusao vivia aqui a vontade
            # — o proprio caso «a falha traz codigo declarado» reprovava.
            #
            # Os dois nomes passam a conviver, cada um no seu campo, que e
            # exactamente o que a `024` desenha: `diagnostic_code` para a
            # etapa e `canonical_state` para o item.
            etapas.append(_etapa(nome, 'FAIL', entrada, saida=6, passou=6,
                                 erros=4, codigo=dg.RAW_PERSISTENCE_FAILED,
                                 estado_do_item=ESTADO_DO_ITEM,
                                 ms=120))
            ja_falhou = True
            continue
        etapas.append(_etapa(nome, 'PASS', entrada, saida=entrada,
                             passou=entrada, ms=40))
        ultima_boa = nome

    retrato = {
        'RUN_ID': 'DRY-RUN-1', 'STAGE': ONDE_FALHA,
        'DIAGNOSTIC_CODE': dg.RAW_PERSISTENCE_FAILED,
        'CANONICAL_STATE': 'EXECUTOR_UNAVAILABLE',
        'O_QUE_ESTAVA_A_MAO': {'ferramenta': 'pdftotext', 'encontrada': False,
                               'itens_por_processar': 4},
        'PORQUE_ISTO_SE_GUARDA': ('sem o retrato, o diagnostico e uma palavra. '
                                  'Com ele, da para repetir o caso.'),
    }
    corrida = {
        'RUN_ID': 'DRY-RUN-1', 'ROUTE_CLASS_ID': 'RC-DRY',
        'SOURCE_ID': 'FONTE-DE-MENTIRA', 'RUN_STATE': 'FAILED',
        'LAST_GOOD_STAGE': ultima_boa,
        'RESUME_SAFE': 'RESUME_SAFE',
        'POLICY_VERSION': 'dry/1', 'CODE_VERSION': 'dry/1',
        'COST': 0, 'COST_UNIT': 'nenhuma', 'DURATION_MS': 200,
    }
    return corrida, etapas, retrato


def retomada(corrida):
    """Retomar continua da ultima boa. NAO recomeca."""
    i = ETAPAS.index(corrida['LAST_GOOD_STAGE'])
    return {'COMECA_EM': ETAPAS[i + 1],
            'NAO_REPETE': list(ETAPAS[:i + 1]),
            'PORQUE': ('recomecar criaria uma SEGUNDA corrida. Ja aconteceu '
                       'nesta casa: um relatorio rebentou depois de a producao '
                       'estar correta, e a tentacao foi correr tudo outra vez.')}


def main():
    corrida, etapas, retrato = corrida_que_falha_no_meio()
    print('O FLUXO NO SECO — sem rede, sem producao, sem ficheiro')
    print('')
    print('  %-11s %-9s %5s %5s %5s %5s  %s'
          % ('ETAPA', 'ESTADO', 'ENT', 'PASS', 'ERR', 'N/RUN', 'DIAGNOSTICO'))
    for e in etapas:
        print('  %-11s %-9s %5s %5s %5s %5s  %s'
              % (e['STAGE'], e['STAGE_STATE'], e['INPUT_COUNT'], e['PASSED'],
                 e['ERROR'], e['NOT_RUN'], e['DIAGNOSTIC_CODE'] or ''))
    print('')

    checks = []
    montante = [e for e in etapas
                if ETAPAS.index(e['STAGE']) < ETAPAS.index(ONDE_FALHA)]
    jusante = [e for e in etapas
               if ETAPAS.index(e['STAGE']) > ETAPAS.index(ONDE_FALHA)]
    falhou = next(e for e in etapas if e['STAGE'] == ONDE_FALHA)

    checks.append(('a montante passou',
                   all(e['STAGE_STATE'] == 'PASS' for e in montante)))
    checks.append(('a etapa do meio falhou',
                   falhou['STAGE_STATE'] == 'FAIL'))
    checks.append(('a falha traz codigo declarado',
                   falhou['DIAGNOSTIC_CODE'] in t.CODIGOS_DE_DIAGNOSTICO))
    checks.append(('a jusante e NOT_RUN, e NAO FAIL',
                   all(e['STAGE_STATE'] == 'NOT_RUN' for e in jusante)))
    checks.append(('nenhuma etapa a jusante foi contada como erro',
                   all(e['ERROR'] == 0 for e in jusante)))
    checks.append(('ha retrato do momento da falha',
                   bool(retrato['O_QUE_ESTAVA_A_MAO'])))
    checks.append(('LAST_GOOD_STAGE aponta a ultima que passou',
                   corrida['LAST_GOOD_STAGE'] == montante[-1]['STAGE']))
    r = retomada(corrida)
    checks.append(('retomar comeca onde parou',
                   r['COMECA_EM'] == ONDE_FALHA))
    checks.append(('retomar nao repete o que ja estava feito',
                   r['NAO_REPETE'] == list(ETAPAS[:ETAPAS.index(ONDE_FALHA)])))
    checks.append(('a conta fecha em todas as etapas, mesmo com a falha',
                   all(e['UNACCOUNTED_INPUT'] == 0 for e in etapas)))

    for nome, ok in checks:
        print('  %s  %s' % ('OK  ' if ok else 'FALHA', nome))
    print('')
    bom = all(ok for _n, ok in checks)
    print('FLUXO_NO_SECO=%s' % ('PASS' if bom else 'FAIL'))
    print('  o que isto prova: a telemetria distingue NAO CORREU de FALHOU, e')
    print('  a conta fecha mesmo quando o fluxo nao fecha. 100% nao precisa')
    print('  chegar — precisa ser explicado.')
    return 0 if bom else 1


if __name__ == '__main__':
    sys.exit(main())
