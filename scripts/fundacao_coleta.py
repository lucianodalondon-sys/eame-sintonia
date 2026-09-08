#!/usr/bin/env python3
"""COLLECTION_FOUNDATION_CLOSED — o portão onde as duas linhas se encontram.

    python3 scripts/fundacao_coleta.py
    python3 scripts/fundacao_coleta.py --build
    python3 scripts/fundacao_coleta.py --json

POR QUE ESTE ARQUIVO EXISTE
----------------------------
Existiam dois portões medidos, e nenhum dos dois respondia à pergunta que a
missão faz:

    EAME_COLLECTION_ENTRY_GATE  responde «o EAME PODE ABRIR coleta?»
                                Hoje READY, 35/35 cicatrizes PROVED.
    FRONTEIRA_ATRAVESSADA       responde «o que se coletou CHEGA?»
                                Hoje NÃO, quatro famílias abertas.

A pergunta da fundação é a terceira, e é a conjunção das duas:

    A COLETA ESTÁ FUNDADA QUANDO SE PODE COLETAR **E** O QUE SE COLETA CHEGA.

Um portão de entrada READY sozinho autorizaria coletar mais para dentro de um
funil que não entrega — o modo de falha mais caro que existe aqui, porque cada
rodada paga produz acervo e o acervo não vira inteligência. Por isso a fundação
não herda o READY da entrada: ela o EXIGE, e exige mais.

O QUE «FECHADA» SIGNIFICA, E O QUE NÃO SIGNIFICA
-------------------------------------------------
    SIGNIFICA      pode-se abrir coleta recorrente sabendo que o produto dela
                   atravessa até a tela, e que a perda em cada fronteira tem
                   medidor, dono e ação mínima.
    NÃO SIGNIFICA  que o acervo está completo, que as fontes são suficientes,
                   ou que a inteligência é boa. Fundação é chão, não teto.

A REGRA QUE ESTE ARQUIVO NÃO PODE VIOLAR
-----------------------------------------
Da seção I do RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA, onde esta linhagem
publicou ZERO no lugar de NÃO MEDIDO DAQUI:

    NÃO MEDIDO NÃO É ZERO, E NÃO MEDIDO NÃO É FECHADO.

Um pilar que não pôde ser medido daqui entra como NAO_MEDIDO e **impede** o
fechamento — exatamente como um pilar reprovado. A diferença entre os dois
aparece no motivo, nunca no resultado: chamar de fechado o que não se mediu é
a mesma mentira que chamar de zero o que não se contou, só que para cima.

A SAÍDA FÁCIL, FECHADA
-----------------------
A edição tentadora de amanhã é tirar o pilar da TRAVESSIA da lista e colher
SIM sem que nenhuma família tenha atravessado. `tests/test_fundacao_coleta.py`
reprova essa edição, pela mesma razão e no mesmo formato com que
`tests/test_portoes_eame.py` reprova tirar LOCALIZACAO do portão da coleta.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import portoes_eame as PORTOES                                    # noqa: E402

# A data da missao, fixa. Nao e a data de hoje de proposito: um artefato
# derivado tem de sair byte-identico quando as entradas nao mudam, e um
# carimbo de relogio faria cada regeracao parecer um facto novo.
DATA_DA_MISSAO = '2026-09-08'

SAIDA = os.path.join(RAIZ, 'data', 'samples', 'FUNDACAO-DA-COLETA.json')
FRONTEIRA = os.path.join(RAIZ, 'data', 'samples', 'FRONTEIRA-ACERVO-PACOTE.json')
MEDIDOR_DA_FRONTEIRA = os.path.join(
    RAIZ, 'italia-portale', 'audit', 'fronteira-acervo-pacote.mjs')


# ── OS PILARES ────────────────────────────────────────────────────────
# Cada pilar declara de QUEM ele deriva. Nenhum é escrito à mão, e nenhum
# aceita como entrada uma frase de documento: todos leem a saída de um
# medidor executável, e o medidor está nomeado aqui.
PILARES = {
    'ENTRADA': {
        'PERGUNTA': 'o EAME pode abrir coleta em geral?',
        'MEDIDOR': 'scripts/portoes_eame.py',
        'DERIVA_DE': 'EAME_COLLECTION_ENTRY_GATE',
        'PORQUE_E_PILAR':
            'coletar sem o portão de entrada é produzir registro sem lugar de '
            'fato, sem identidade estável e sem retomada — dívida que só '
            'aparece quando já custou.',
    },
    'PRESERVACAO': {
        'PERGUNTA': 'o bruto que já foi coletado sobrevive e confere?',
        'MEDIDOR': 'scripts/portoes_eame.py',
        'DERIVA_DE': 'RAW_PRESERVATION_GATE + RAW_CONTENT_INTEGRITY_GATE',
        'PORQUE_E_PILAR':
            'coleta cujo bruto não sobrevive não é coleta: é uma afirmação '
            'sobre o passado sem a evidência que a sustenta.',
    },
    'TRAVESSIA': {
        'PERGUNTA': 'o que se coletou atravessa a ingestão até o artefato da tela?',
        'MEDIDOR': 'italia-portale/audit/fronteira-acervo-pacote.mjs',
        'DERIVA_DE': 'FRONTEIRA_ATRAVESSADA',
        'PORQUE_E_PILAR':
            'este é o pilar que a entrada não cobre, e é o ponto de perda '
            'principal medido pelo CHECKPOINT desta linhagem. Sem ele, '
            'COLLECTION_FOUNDATION_CLOSED significaria apenas «podemos '
            'começar», e a missão não pergunta isso.',
    },
}


def _portoes():
    return PORTOES.monta()


def _fronteira():
    """A travessia, lida do artefato — e o artefato precisa ser corrente.

    Um artefato gravado contra um BUILD_ID que já não é o do portal mede
    outra safra. Isso não é medição desatualizada: é medição de outra coisa.
    Por isso o pilar é NAO_MEDIDO quando o artefato falta, e o medidor é
    reexecutado para conferir a safra quando `node` existe.
    """
    if not os.path.exists(FRONTEIRA):
        return None, ('o artefato da fronteira não existe. Rode: node %s --build'
                      % os.path.relpath(MEDIDOR_DA_FRONTEIRA, RAIZ))
    with open(FRONTEIRA, encoding='utf-8') as h:
        d = json.load(h)
    return d, None


def _confere_a_safra(d):
    """NÃO MEDIDO DAQUI é resposta. Silêncio não é.

    Se `node` não existe neste ambiente, não se pode reexecutar o medidor —
    e então não se pode afirmar que o artefato no disco corresponde ao
    artefato que o portal carrega hoje. A resposta é NAO_CONFERIDA, com o
    motivo escrito, e não «confere».
    """
    try:
        r = subprocess.run(['node', MEDIDOR_DA_FRONTEIRA, '--json'],
                           capture_output=True, text=True, timeout=300, cwd=RAIZ)
    except (OSError, subprocess.SubprocessError) as e:
        return {'CONFERIDA': 'NAO', 'PORQUE': 'medidor não executável aqui: %s' % e}
    if r.returncode != 0:
        return {'CONFERIDA': 'NAO', 'PORQUE': 'o medidor falhou: %s' % r.stderr.strip()[:200]}
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


def avalia():
    p = _portoes()
    fronteira, faltou = _fronteira()

    pilares = {}

    # ── ENTRADA ────────────────────────────────────────────────────────
    entrada = p['PORTOES']['EAME_COLLECTION_ENTRY_GATE']
    pilares['ENTRADA'] = dict(PILARES['ENTRADA'], **{
        'ESTADO': 'FECHADO' if entrada['ESTADO'] == 'READY' else 'ABERTO',
        'MEDIDO': 'SIM',
        'EVIDENCIA': '%s · %s de %s cicatrizes PROVED' % (
            entrada['ESTADO'], entrada['CICATRIZES_PROVED'],
            entrada['CICATRIZES_COBERTAS']),
        'BLOQUEADORES': [b['ID'] for b in entrada['BLOQUEADORES']],
    })

    # ── PRESERVACAO ────────────────────────────────────────────────────
    raw = p.get('RAW_PRESERVATION_GATE', {})
    estado_raw = raw.get('ESTADO')
    integridade = raw.get('RAW_CONTENT_INTEGRITY_GATE')
    ok_raw = estado_raw == 'CLOSED' and integridade == 'CLOSED'
    pilares['PRESERVACAO'] = dict(PILARES['PRESERVACAO'], **{
        'ESTADO': 'FECHADO' if ok_raw else ('NAO_MEDIDO' if estado_raw is None else 'ABERTO'),
        'MEDIDO': 'NAO' if estado_raw is None else 'SIM',
        'EVIDENCIA': 'RAW_PRESERVATION=%s · RAW_CONTENT_INTEGRITY=%s' % (
            estado_raw, integridade),
        'BLOQUEADORES': [] if ok_raw else ['RAW_PRESERVATION_GATE'],
        'VERIFICADO_DAQUI': raw.get('VERIFICADO_DAQUI', 'NAO'),
        'NOTA':
            'a prova desta preservação é EXTERNA: foi produzida na máquina que '
            'tem credencial. Este ambiente não recontou, e recontar daqui '
            'produziria zero — que é o defeito, não a medida.',
    })

    # ── TRAVESSIA ──────────────────────────────────────────────────────
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
                for f in fronteira['FAMILIAS'] if f['ESTADO'] != 'FECHADA'],
        })

    # ── A CONJUNÇÃO ────────────────────────────────────────────────────
    # SIM exige TODO pilar FECHADO. NAO_MEDIDO não fecha — pela mesma razão
    # que NÃO MEDIDO não é zero.
    abertos = [n for n, v in pilares.items() if v['ESTADO'] != 'FECHADO']
    fechada = not abertos

    return {
        'SOURCE_ID': 'FUNDACAO-DA-COLETA',
        'VERSION': 1,
        'captured_at': DATA_DA_MISSAO,
        'SOURCE_LOCATION': 'interno',
        'FACT_LOCATION': 'EAME',
        'ORIGINAL_LANGUAGE': 'pt',
        'DERIVADO_DE': ['scripts/portoes_eame.py',
                        'italia-portale/audit/fronteira-acervo-pacote.mjs',
                        'data/samples/FRONTEIRA-ACERVO-PACOTE.json'],
        'O_QUE_ISTO_E':
            'a conjunção dos pilares da fundação da coleta, derivada de '
            'medidores executáveis. Nenhum estado deste arquivo foi digitado.',
        'O_QUE_ISTO_NAO_E':
            'não é um juízo sobre a qualidade da inteligência, nem sobre a '
            'suficiência das fontes. Fundação é chão, não teto.',
        'PERGUNTA':
            'o EAME pode abrir coleta recorrente sabendo que o produto dela '
            'atravessa até a tela?',
        'PILARES': pilares,
        'COLLECTION_FOUNDATION_CLOSED': 'SIM' if fechada else 'NAO',
        'PILARES_ABERTOS': abertos,
        'O_QUE_FALTA_PARA_SIM': [
            {'PILAR': n, 'ESTADO': pilares[n]['ESTADO'],
             'BLOQUEADORES': pilares[n]['BLOQUEADORES'],
             'DONO': pilares[n].get('DONO', 'esta linhagem')}
            for n in abertos],
        'REGRA': 'NÃO MEDIDO NÃO É ZERO, E NÃO MEDIDO NÃO É FECHADO.',
        'ONDE_AS_DUAS_LINHAS_SE_ENCONTRAM':
            'docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md — a linha paralela '
            'escreve contra este portão, e ele é a condição de encontro.',
    }


def monta():
    return avalia()


def _imprime(d):
    print('')
    print('  A FUNDAÇÃO DA COLETA')
    print('  ' + '-' * 74)
    for nome, p in d['PILARES'].items():
        print('  %-14s %-12s %s' % (nome, p['ESTADO'], p['EVIDENCIA']))
        for b in p['BLOQUEADORES']:
            print('  %-14s %-12s   bloqueia: %s' % ('', '', b))
    print('  ' + '-' * 74)
    print('  COLLECTION_FOUNDATION_CLOSED = %s' % d['COLLECTION_FOUNDATION_CLOSED'])
    if d['PILARES_ABERTOS']:
        print('  pilares abertos: %s' % ' · '.join(d['PILARES_ABERTOS']))
    print('')
    for a in d['O_QUE_FALTA_PARA_SIM']:
        print('  falta em %s (%s) — dono: %s' % (a['PILAR'], a['ESTADO'], a['DONO']))
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
