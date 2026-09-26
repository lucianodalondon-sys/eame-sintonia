#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ANTES/DEPOIS dos extractores T6 (local, periodo, molecula) — as MESMAS respostas guardadas.

    py ferramentas/t6_para_sala/antes_depois_extratores.py --rodadas=<pasta> --antes=<commit> --para=<json>

ANTES = `coleta/pesquisadores_t6.py` no commit dado (lido com `git show`, nunca editado);
DEPOIS = o da arvore. Os dois leem a mesma pasta de rodadas (sem rede). Conta por trabalho,
lista cada mudanca, e separa uma AMOSTRA fixa (as primeiras 20 mudancas por DOI) para ler
a mao — a amostra e escolhida pela ordem, nao pelo resultado.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
CAMPOS = ('LOCAL_DO_ESTUDO_ESCRITO', 'PERIODO_DO_ESTUDO', 'MOLECULA')
NS = 'NAO SEI'


def _modulo(nome, caminho):
    sp = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _curto(campo, v):
    if v == NS:
        return NS
    if campo == 'LOCAL_DO_ESTUDO_ESCRITO':
        return ['%s/%s' % (x['VALOR'], x['PRECISAO']) for x in v]
    if campo == 'PERIODO_DO_ESTUDO':
        return ['%s-%s «%s»' % (x['DE'], x['ATE'], x['TRECHO']) for x in v]
    return [x['VALOR'] for x in v]


def main(argv):
    opt = dict(a[2:].split('=', 1) for a in argv if a.startswith('--') and '=' in a)
    antigo = subprocess.run(['git', '-C', RAIZ, 'show', '%s:coleta/pesquisadores_t6.py' % opt['antes']],
                            capture_output=True, text=True, encoding='utf-8', check=True).stdout
    tmp = os.path.join(tempfile.mkdtemp(prefix='t6-antes-'), 'pesquisadores_t6_antes.py')
    with open(tmp, 'w', encoding='utf-8') as h:
        h.write(antigo.replace("RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
                               "RAIZ = %r" % RAIZ))
    A = _modulo('t6_antes', tmp)
    D = _modulo('t6_depois', os.path.join(RAIZ, 'coleta', 'pesquisadores_t6.py'))
    chave = lambda u: u['DOI'] if u['DOI'] != NS else u['OPENALEX_WORK_ID']  # noqa: E731
    ua = {chave(u): u for u in A.ler_pasta(opt['rodadas'])[0]}
    ud = {chave(u): u for u in D.ler_pasta(opt['rodadas'])[0]}
    tem = lambda u, c: u[c] != NS  # noqa: E731
    conta = {}
    for nome, us in (('ANTES', ua), ('DEPOIS', ud)):
        c = {k: sum(1 for u in us.values() if tem(u, k)) for k in CAMPOS}
        c['CULTURA_PROBLEMA_LOCAL_PERIODO'] = sum(1 for u in us.values() if all(
            tem(u, k) for k in ('CULTURA', 'PROBLEMA', 'LOCAL_DO_ESTUDO_ESCRITO', 'PERIODO_DO_ESTUDO')))
        c['LOCAL_ABAIXO_DO_PAIS'] = sum(1 for u in us.values() if tem(u, 'LOCAL_DO_ESTUDO_ESCRITO') and any(
            x['PRECISAO'] in ('REGIAO', 'PROVINCIA') for x in u['LOCAL_DO_ESTUDO_ESCRITO']))
        c['TRABALHOS'] = len(us)
        conta[nome] = c
    mudancas = []
    for doi in sorted(ud):
        a, d = ua.get(doi), ud[doi]
        dif = {k: {'ANTES': _curto(k, a[k]) if a else NS, 'DEPOIS': _curto(k, d[k])} for k in CAMPOS
               if not a or _curto(k, a[k]) != _curto(k, d[k])}
        if dif:
            mudancas.append({'DOI': doi, 'TITULO': d['TITULO'][:120], 'PUBLICADO_EM': d['PUBLICADO_EM'], 'MUDOU': dif})
    ganhou = {k: sum(1 for m in mudancas if k in m['MUDOU'] and m['MUDOU'][k]['ANTES'] == NS) for k in CAMPOS}
    perdeu = {k: sum(1 for m in mudancas if k in m['MUDOU'] and m['MUDOU'][k]['DEPOIS'] == NS) for k in CAMPOS}
    r = {'RODADAS': opt['rodadas'], 'ANTES_COMMIT': opt['antes'], 'DEPOIS': D.EXTRATOR_VERSAO,
         'LEXICO_MOLECULAS_DEPOIS': len(D.MOLECULAS_REGISTO), 'CONTAGENS': conta,
         'TRABALHOS_QUE_MUDARAM': len(mudancas), 'GANHOU_CAMPO': ganhou, 'PERDEU_CAMPO': perdeu,
         'AMOSTRA_PARA_LER_A_MAO': mudancas[:20], 'TODAS_AS_MUDANCAS': mudancas}
    with open(opt['para'], 'w', encoding='utf-8', newline='\n') as h:
        json.dump(r, h, ensure_ascii=False, indent=1)
    print(json.dumps({k: r[k] for k in ('CONTAGENS', 'TRABALHOS_QUE_MUDARAM', 'GANHOU_CAMPO', 'PERDEU_CAMPO',
                                        'LEXICO_MOLECULAS_DEPOIS')}, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
