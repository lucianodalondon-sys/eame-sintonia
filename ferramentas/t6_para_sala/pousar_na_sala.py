#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""POUSAR OS TRABALHOS T6 NA SALA — o botao canonico, com a persistencia da PRODUCAO.

    py ferramentas/t6_para_sala/pousar_na_sala.py --rodadas=<pasta das rodadas> --confirmo [--universo=T5]

E o MESMO programa no ensaio (copia da Sala, Postgres descartavel) e na Sala real: so muda o
ambiente. Exige as quatro variaveis da porta canonica desta maquina:

    SINTONIA_COLLECTION_DSN   o banco da Collection (raw_asset, collection_run)
    SINTONIA_SALA_BACKEND     POSTGRES
    SINTONIA_SALA_DSN         o banco da Sala
    SINTONIA_ARMAZEM_RAIZ     onde os bytes do bruto ficam (absoluta, fora da arvore)
    (+ SINTONIA_PSQL_EXE)

O que faz: copia as respostas das rodadas para o balcao do executor (sem rede), e aperta
`orquestrador.correr(Pedido(alvo="T6", universo=...))` com a memoria, o rastro e a raiz dos
bytes que `orquestrador/persistencia.dependencias_do_runtime()` monta — o que a porta CLI faz.
Recusa correr se a Sala nao estiver CANONICA (backend de ficheiro = escreve no sitio errado)
ou sem `--confirmo`. Nao escreve a mao em tabela nenhuma.
"""
import json
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import sala_de_espera as espera                     # noqa: E402
from pedido import Pedido                           # noqa: E402


def main(argv):
    opt = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '1') for a in argv if a.startswith('--'))
    universo = opt.get('universo', 'T5')
    if 'confirmo' not in opt:
        print('RECUSADO: falta --confirmo (isto escreve na Sala do ambiente)')
        return 2
    est = espera.estado_operacional()
    if not est.get('CANONICO'):
        print('RECUSADO: a Sala deste ambiente nao e canonica: %s' % json.dumps(est, ensure_ascii=False))
        return 2
    import persistencia
    per = persistencia.dependencias_do_runtime(dict(os.environ))
    if per.ESTADO != persistencia.OPERACIONAL:
        print('RECUSADO: persistencia %s (%s) — so corre em modo OPERACIONAL' % (per.ESTADO, per.PORQUE))
        return 2
    balcao = os.path.join(RAIZ, 'data', 'colheita', 'pesquisadores-t6', 'rodadas')
    if opt.get('rodadas') and os.path.abspath(opt['rodadas']) != os.path.abspath(balcao):
        os.makedirs(balcao, exist_ok=True)
        for f in os.listdir(opt['rodadas']):
            if f.endswith('.json') and (f.startswith(('openalex-', 'crossref-', 'orcid-')) or f == 'ESTADO.json'):
                shutil.copy2(os.path.join(opt['rodadas'], f), os.path.join(balcao, f))
    import orquestrador as orq
    p = Pedido(alvo='T6', filtros={'pais': 'IT', 'universo': universo})
    recibo = orq.correr(p, memoria=per.memoria, banco_do_rastro=per.banco_do_rastro,
                        raiz_do_armazem=per.raiz_do_armazem)
    recibo.pop('_plano', None)
    porta = recibo.get('PORTA') or {}
    ing = recibo.get('INGRESSO') or {}
    print(json.dumps({'UNIVERSO': universo, 'RUN_ID': recibo.get('RUN_ID'), 'STATUS': recibo.get('STATUS'),
                      'PERSISTENCIA': per.para_json(), 'COLHEITA': recibo.get('COLHEITA_ENCONTRADA'),
                      'INGRESSO': {k: ing.get(k) for k in ('PRESERVADOS', 'RECUSADOS', 'RUN_STATE', 'FONTE_PROVADA')},
                      'ADMISSAO': porta.get('por_resultado'), 'PRONTOS': porta.get('prontos'),
                      'ESPERA': porta.get('espera'), 'RECIBO_DA_SALA': porta.get('recibo') or porta.get('RECIBO'),
                      'ERRO': (recibo.get('ERROR') or '')[:400]}, ensure_ascii=False, indent=1, default=str))
    return 0 if recibo.get('STATUS') == 'SUCCESS' else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
