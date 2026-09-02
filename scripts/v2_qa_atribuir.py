#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRIBUI O ESTADO DE QA a cada um dos 321 registros da last-mile.

    python3 scripts/v2_qa_atribuir.py

    QA_PASS        sobreviveu à conferência independente, sem mudança
    QA_CORRECTED   a conferência achou defeito e o registro foi RECONSTRUÍDO
    QA_UNREVIEWED  fonte externa real, mas sem segunda passada
    QA_REJECTED    a alegação não sobrevive na forma atual

COMO O CASAMENTO É POSSÍVEL
----------------------------
O conferente recebeu as N PRIMEIRAS linhas do bloco (`registros.slice(0,8)` no
primeiro fluxo, `slice(0,6)` no segundo) e devolveu cada derrubado começando
com `[k]` — a posição na amostra, base 1. Isso torna o casamento determinístico,
não uma adivinhação por texto parecido.

⚠️ A REGRA QUE IMPEDE UM QA_PASS FALSO
---------------------------------------
Em dois blocos o conferente derrubou MAIS do que listou: no ISTAT, 6
verificados e 1 confirmado dão 5 quedas, mas só 4 vieram identificadas. Há uma
queda cujo alvo não sabemos.

    QUANDO SOBRA UMA QUEDA SEM DONO, NINGUÉM NAQUELE BLOCO GANHA QA_PASS.

Os não identificados daquele bloco descem para QA_UNREVIEWED. Chamar de
aprovado um registro que pode ser justamente o que caiu seria o pior erro
possível deste portão — ele existe para impedir alegação insegura, e um
QA_PASS falso é exatamente isso.

⚠️ E A OUTRA: FORA DA AMOSTRA NÃO É APROVADO
---------------------------------------------
Dos 321, só 104 foram à conferência. Os outros 217 são registros externos
reais — e nada mais. `QA_UNREVIEWED` não é demérito: é a descrição exata do
que sabemos. O que ele proíbe é gerar afirmação de tela sozinho.
"""
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, '.tmp')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-V2')

# quantos registros cada fluxo mandou para a conferência
AMOSTRA = {'lastmile1.json': 8, 'lastmile2.json': 6}


def indices_derrubados(derrubados, teto):
    """→ (set de índices 0-based, quantos não deram para identificar)."""
    idx, orfaos = set(), 0
    for d in derrubados:
        txt = (d.get('o_que') or '')
        # «[3] ...» ou «Registro [8] ...» ou «[2], [3], [4], [5] e [6] ...»
        achados = [int(n) for n in re.findall(r'\[(\d{1,2})\]', txt[:90])]
        achados = [n for n in achados if 1 <= n <= teto]
        if achados:
            idx.update(n - 1 for n in achados)
        else:
            orfaos += 1
    return idx, orfaos


def main():
    registros, blocos = [], {}
    for arq, teto in AMOSTRA.items():
        p = os.path.join(TMP, arq)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for b in d['blocos']:
            nome = b['bloco']
            c = b.get('verificacao') or {}
            ver = c.get('verificados', 0)
            conf = c.get('confirmados', 0)
            dr = c.get('derrubados') or []
            caidos, orfaos = indices_derrubados(dr, teto)
            quedas_reais = max(0, ver - conf)
            # ⚠️ a trava: queda sem dono contamina o bloco inteiro amostrado
            sem_dono = quedas_reais - len(caidos)
            blocos[nome] = {
                'BLOCO': nome, 'FLUXO': arq, 'TETO_DA_AMOSTRA': teto,
                'REGISTROS': b['n_registros'], 'VERIFICADOS': ver,
                'CONFIRMADOS': conf, 'QUEDAS_REAIS': quedas_reais,
                'QUEDAS_IDENTIFICADAS': len(caidos),
                'QUEDAS_SEM_DONO': max(0, sem_dono),
                'DERRUBADOS_ORFAOS': orfaos,
                'INDICES_CAIDOS': sorted(caidos),
                'DERRUBADOS': dr,
            }
            for i, r in enumerate(b.get('registros', [])):
                if i in caidos:
                    qa, porque = 'PENDENTE_DE_DECISAO', \
                        'a conferencia derrubou; falta decidir REJEITAR ou RECONSTRUIR'
                elif i < min(teto, ver) and sem_dono <= 0:
                    qa, porque = 'QA_PASS', \
                        'foi a conferencia independente e sobreviveu sem mudanca'
                elif i < min(teto, ver):
                    qa, porque = 'QA_UNREVIEWED', \
                        ('foi a conferencia, mas o bloco tem %d queda(s) sem dono '
                         'identificado — este registro pode ser uma delas' % sem_dono)
                else:
                    qa, porque = 'QA_UNREVIEWED', \
                        'nao foi a segunda passada. Registro externo real, nada mais.'
                registros.append(dict(
                    r, BLOCO=nome, INDICE_NO_BLOCO=i, FLUXO=arq,
                    QA_STATUS=qa, QA_POR_QUE=porque,
                    FOI_A_CONFERENCIA=i < min(teto, ver)))

    conta = Counter(r['QA_STATUS'] for r in registros)
    os.makedirs(SAIDA, exist_ok=True)
    saida = {
        'DATASET': 'IT-V2-QA-ATRIBUIDO',
        'O_QUE_E': 'os 321 registros da last-mile, cada um com estado de QA',
        'LEI_DO_CASAMENTO':
            'o conferente recebeu as N primeiras linhas do bloco e devolveu cada '
            'derrubado comecando com [k], a posicao na amostra. O casamento e '
            'deterministico, nao por semelhanca de texto.',
        'LEI_DA_QUEDA_SEM_DONO':
            'quando o conferente derruba mais do que lista, ninguem naquele bloco '
            'ganha QA_PASS. Um QA_PASS falso e exatamente o que este portao existe '
            'para impedir.',
        'TAXA_MEDIDA_DA_CONFERENCIA': {
            'VERIFICADOS': sum(b['VERIFICADOS'] for b in blocos.values()),
            'CONFIRMADOS': sum(b['CONFIRMADOS'] for b in blocos.values()),
            'QUEDAS': sum(b['QUEDAS_REAIS'] for b in blocos.values()),
            'IDENTIFICADAS': sum(b['QUEDAS_IDENTIFICADAS'] for b in blocos.values()),
            'SEM_DONO': sum(b['QUEDAS_SEM_DONO'] for b in blocos.values()),
        },
        'POR_ESTADO': dict(conta),
        'BLOCOS': list(blocos.values()),
        'REGISTROS': registros,
    }
    p = os.path.join(SAIDA, 'IT-V2-QA-ATRIBUIDO.json')
    json.dump(saida, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    t = saida['TAXA_MEDIDA_DA_CONFERENCIA']
    print('conferencia: %d verificados · %d confirmados · %d quedas '
          '(%d identificadas, %d sem dono)'
          % (t['VERIFICADOS'], t['CONFIRMADOS'], t['QUEDAS'],
             t['IDENTIFICADAS'], t['SEM_DONO']))
    print('taxa medida de falha: %.0f%%' % (100.0 * t['QUEDAS'] / max(1, t['VERIFICADOS'])))
    print()
    for k, v in conta.most_common():
        print('  %-22s %d' % (k, v))
    print()
    print('%-28s %4s %4s %4s %5s %5s' % ('BLOCO', 'REG', 'VER', 'CONF', 'IDENT', 'ORFA'))
    for b in blocos.values():
        marca = '  <== queda sem dono' if b['QUEDAS_SEM_DONO'] else ''
        print('%-28s %4d %4d %4d %5d %5d%s'
              % (b['BLOCO'][:28], b['REGISTROS'], b['VERIFICADOS'], b['CONFIRMADOS'],
                 b['QUEDAS_IDENTIFICADAS'], b['QUEDAS_SEM_DONO'], marca))
    print()
    print('gravado:', os.path.relpath(p, ROOT))


if __name__ == '__main__':
    main()
