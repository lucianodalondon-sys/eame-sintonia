#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O CONTRATO DE SUPERFICIE DE UMA FAMILIA — lido por quem nao decide nada.

    python3 scripts/it_contrato_de_familia.py SINAIS_DE_CAMPO
    python3 scripts/it_contrato_de_familia.py --todas

POR QUE ESTE ARQUIVO EXISTE
----------------------------
O acervo italiano tem 98,6% dos registos com proveniencia e data, e 3.941
NAO SEI ja declarados. O que falta as familias nao e publicabilidade: e
alguem dizer o que a tela faz com elas.

    O BLOQUEIO NUNCA FOI «PODE APARECER?». FOI «APARECER COMO O QUE?».

Uma familia sem contrato nao esta proibida — esta por decidir, e enquanto
estiver por decidir cada consumidor inventa a sua regra e todos acham que
estao a obedecer.

O QUE ESTE CONSUMIDOR FAZ
-------------------------
Abre o contrato da familia, obedece literalmente, e conta nos artefactos. Se
para montar a superficie precisar de UMA decisao que o contrato nao declarou —
inclusive um ficheiro da familia que nenhum subconjunto reclama — reprova.

    UM FICHEIRO QUE NENHUM SUBCONJUNTO RECLAMA E UMA DECISAO POR TOMAR
    DISFARCADA DE DADO.

Ele NAO reclassifica dados, NAO cria QA que nao existe e NAO usa CLIENT_SAFE
como portao geral — CLIENT_SAFE responde se a afirmacao se sustenta como FATO
sem a nossa sintese, e isso nao decide visibilidade.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
CONTRATOS = os.path.join(SAMPLES, 'IT-PORTAL-V1')
SAIDA = os.path.join(CONTRATOS, 'IT-FAMILIA-SUPERFICIE-VERIFICACAO-V1.json')

DESTINOS = ('CARTAO', 'COM_METODO', 'FORA')


def _maior(doc):
    """A maior lista de dicionarios do documento. Serve as familias de corpus,
    onde cada ficheiro traz a sua lista com nome proprio (SPEAKERS, FINDINGS,
    EPISODES, ATTEMPTS) e uma lista branca de chaves conta 1 onde ha 14."""
    if isinstance(doc, list):
        return doc
    if not isinstance(doc, dict):
        return []
    melhor = []
    for v in doc.values():
        if isinstance(v, list) and v and isinstance(v[0], dict) and len(v) > len(melhor):
            melhor = v
    return melhor or [doc]


def _lista(doc, chave):
    if chave == '(doc unico)':
        return [doc]
    v = doc.get(chave) if isinstance(doc, dict) else None
    return v if isinstance(v, list) else []


def uma(familia):
    p = os.path.join(CONTRATOS, 'IT-CONTRATO-FAMILIA-%s-V1.json' % familia)
    if not os.path.exists(p):
        return {'FAMILIA': familia, 'CONTRATO': 'AUSENTE',
                'DECISOES_QUE_O_PORTAL_TERIA_DE_ADIVINHAR': ['nao existe contrato para esta familia']}
    C = json.load(open(p, encoding='utf-8'))
    falhas, passos = [], []

    def exige(cond, chave, detalhe):
        passos.append({'PERGUNTA': chave, 'RESPONDIDA': bool(cond), 'DETALHE': detalhe})
        if not cond:
            falhas.append('%s · %s' % (chave, detalhe))

    exige(bool(C.get('DONO_DA_DECISAO')), 'QUEM_DECIDE', 'DONO_DA_DECISAO ausente')
    interno = C.get('CAMPOS_QUE_NUNCA_ATRAVESSAM') or []
    exige(isinstance(interno, list), 'O_QUE_NUNCA_ATRAVESSA', 'lista ausente')

    subs = C.get('SUBCONJUNTOS') or []
    exige(bool(subs), 'QUAIS_SUBCONJUNTOS', 'nenhum subconjunto declarado')

    conta = {d: 0 for d in DESTINOS}
    reclamados, detalhe_sub = set(), []
    for s in subs:
        nome, fic, chave = s.get('NOME'), s.get('FICHEIRO'), s.get('CHAVE_DA_LISTA')
        dest = s.get('DESTINO')
        if dest not in DESTINOS:
            falhas.append('DESTINO_INVALIDO · %s tem DESTINO=%r' % (nome, dest))
            continue
        if not s.get('PORQUE'):
            falhas.append('SEM_PORQUE · %s nao diz porque vai para %s' % (nome, dest))
        # Um subconjunto reclama UM ficheiro ou UM PADRAO de caminho. O padrao
        # existe porque uma familia de corpus tem dezenas de ficheiros iguais em
        # forma, e declarar 58 subconjuntos identicos nao e contrato: e ruido
        # que ninguem revê.
        regs, ficheiros_do_sub = [], []
        if s.get('PADRAO'):
            prx = re.compile(s['PADRAO'], re.I)
            for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
                for nn in sorted(nomes):
                    if not nn.endswith('.json'):
                        continue
                    q = os.path.join(base, nn)
                    if not prx.search(q):
                        continue
                    ficheiros_do_sub.append(q)
                    try:
                        d = json.load(open(q, encoding='utf-8'))
                    except Exception:
                        falhas.append('ILEGIVEL · %s' % os.path.relpath(q, ROOT))
                        continue
                    regs.extend(_lista(d, chave) if chave != '(maior lista)'
                                else _maior(d))
            if not ficheiros_do_sub:
                falhas.append('PADRAO_SEM_FICHEIRO · %s' % nome)
        else:
            fp = os.path.join(SAMPLES, fic)
            if not os.path.exists(fp):
                falhas.append('FICHEIRO_AUSENTE · %s' % fic)
                continue
            ficheiros_do_sub = [fp]
            regs = _lista(json.load(open(fp, encoding='utf-8')), chave)
        for q in ficheiros_do_sub:
            reclamados.add(os.path.normpath(q))
        n = len(regs)
        if s.get('N_ESPERADO') != n:
            falhas.append('CONTAGEM · %s: %d, contrato diz %s' % (nome, n, s.get('N_ESPERADO')))
        conta[dest] += n
        detalhe_sub.append({'NOME': nome, 'DESTINO': dest, 'N': n})

        if dest == 'FORA':
            continue
        # campos minimos existem em TODO registo? (ausencia de VALOR e permitida)
        minimos = s.get('CAMPOS_MINIMOS') or []
        if not minimos:
            falhas.append('SEM_CAMPOS_MINIMOS · %s vai a tela sem dizer o que o cartao precisa' % nome)
        faltam = sorted({c for r in regs if isinstance(r, dict)
                         for c in minimos if c not in r})
        if faltam:
            falhas.append('CAMPO_MINIMO_AUSENTE · %s: %s' % (nome, faltam[:4]))
        # como se renderiza o que nao se sabe
        if not (s.get('NAO_SEI') or {}).get('COMO_RENDERIZAR'):
            falhas.append('SEM_REGRA_DE_NAO_SEI · %s nao diz como mostrar o que nao se sabe' % nome)
        if dest == 'COM_METODO' and not s.get('AVISO'):
            falhas.append('SEM_AVISO · %s vai COM_METODO e nao declara o aviso' % nome)
        # nada interno atravessa
        vaza = sorted({c for r in regs if isinstance(r, dict) for c in interno if c in r})
        if vaza and not s.get('REMOVE_INTERNOS'):
            falhas.append('CAMPO_INTERNO_ATRAVESSA · %s: %s (declare REMOVE_INTERNOS)' % (nome, vaza))

    # ── o teste que impede o contrato de fingir cobertura ───────────────────
    rx = re.compile(C.get('REGEX_DA_FAMILIA', '$^'), re.I)
    orfaos = []
    for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
        for n in nomes:
            if not n.endswith('.json'):
                continue
            fp = os.path.join(base, n)
            if rx.search(fp) and os.path.normpath(fp) not in reclamados:
                orfaos.append(os.path.relpath(fp, ROOT))
    exige(not orfaos, 'TODO_FICHEIRO_TEM_DONO',
          '%d ficheiro(s) da familia que nenhum subconjunto reclama: %s'
          % (len(orfaos), orfaos[:3]))

    abertas = C.get('DECISOES_EM_ABERTO') or []
    exige(not abertas, 'NENHUMA_DECISAO_EM_ABERTO', '%s' % abertas[:3])

    return {
        'FAMILIA': familia,
        'DONO_DA_DECISAO': C.get('DONO_DA_DECISAO'),
        'SURFACE_CONTRACT': 'FAIL' if falhas else 'PASS',
        'PODE_APARECER': conta['CARTAO'],
        'APARECE_COM_METODO': conta['COM_METODO'],
        'FICA_FORA': conta['FORA'],
        'TOTAL': sum(conta.values()),
        'SUBCONJUNTOS': detalhe_sub,
        'UNRESOLVED_SURFACE_DECISIONS': len(falhas),
        'DECISOES_QUE_O_PORTAL_TERIA_DE_ADIVINHAR': falhas,
        'PASSOS': passos,
    }


def main():
    argv = sys.argv[1:]
    if '--todas' in argv or not argv:
        fams = sorted(re.findall(r'IT-CONTRATO-FAMILIA-(.+?)-V1\.json',
                                 ' '.join(os.listdir(CONTRATOS))))
    else:
        fams = argv
    todos = [uma(f) for f in fams]
    os.makedirs(CONTRATOS, exist_ok=True)
    json.dump({'DATASET': 'IT-FAMILIA-SUPERFICIE-VERIFICACAO-V1',
               'FAMILIAS': todos}, open(SAIDA, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('== CONTRATO DE SUPERFICIE POR FAMILIA ==')
    print('  %-18s %6s %8s %10s %7s %9s %s'
          % ('FAMILIA', 'TOTAL', 'CARTAO', 'C/METODO', 'FORA', 'UNRESOLV', 'CONTRATO'))
    for r in todos:
        print('  %-18s %6s %8s %10s %7s %9s %s'
              % (r['FAMILIA'], r.get('TOTAL', '—'), r.get('PODE_APARECER', '—'),
                 r.get('APARECE_COM_METODO', '—'), r.get('FICA_FORA', '—'),
                 r.get('UNRESOLVED_SURFACE_DECISIONS', '—'),
                 r.get('SURFACE_CONTRACT', r.get('CONTRATO'))))
    ruins = [r for r in todos if r.get('SURFACE_CONTRACT') != 'PASS']
    for r in ruins:
        print('\n  %s · o portal teria de adivinhar:' % r['FAMILIA'])
        for f in r['DECISOES_QUE_O_PORTAL_TERIA_DE_ADIVINHAR'][:8]:
            print('   · %s' % f)
    print('\n  gravado: %s' % os.path.relpath(SAIDA, ROOT))
    return 1 if ruins else 0


if __name__ == '__main__':
    raise SystemExit(main())
