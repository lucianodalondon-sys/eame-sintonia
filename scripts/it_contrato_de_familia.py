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

# ⚠️ A PRECEDENCIA VEM DO INVENTARIO, NAO DAQUI. Um contrato que decidisse
# sozinho o que e da sua familia daria um numero diferente do inventario para o
# mesmo ficheiro — e dois contadores a discordar sobre o mesmo acervo e
# exatamente o defeito que o V2 foi escrito para fechar.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from it_acervo_inventario_v2 import (familia as _familia_do_inventario,  # noqa: E402
                                     e_italiano as _italiano_do_inventario)



def _do_escopo(caminho, fam):
    """Mesmo recorte do inventario: italiano E desta familia pela precedencia."""
    rel = os.path.relpath(caminho, ROOT)
    try:
        d = json.load(open(caminho, encoding='utf-8'))
    except Exception:
        return False
    return _italiano_do_inventario(rel, d) and _familia_do_inventario(rel) == fam

def _todas(doc):
    """TODAS as coleccoes do documento, nao a maior.

    A versao anterior devolvia so a maior lista, e isso deixava 86 registos de
    FITOSSANITARIO sem dono enquanto o portao dizia PASS: reclamava o ficheiro
    e contava uma lista. Numa familia de corpus, onde tudo e evidencia, ou se
    reclama tudo ou nao se reclamou nada."""
    if isinstance(doc, list):
        return doc
    if not isinstance(doc, dict):
        return []
    fora = []
    for v in doc.values():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            fora.extend(v)
    # O defeito da V1 era contar 1 onde havia 421 — um ficheiro COM coleccao que
    # a lista branca nao reconhecia. Nao era contar 1 onde ha 1. Um artefacto
    # agregado, sem lista nenhuma, E um registo, e o inventario V2 conta-o com
    # chave propria: aqui vale o mesmo, ou os dois contadores voltam a discordar.
    return fora or [doc]


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
                    if not _do_escopo(q, familia):
                        continue
                    ficheiros_do_sub.append(q)
                    try:
                        d = json.load(open(q, encoding='utf-8'))
                    except Exception:
                        falhas.append('ILEGIVEL · %s' % os.path.relpath(q, ROOT))
                        continue
                    regs.extend(_lista(d, chave) if chave != '(todas as listas)'
                                else _todas(d))
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
            reclamados.add((os.path.normpath(q), chave))
        n = len(regs)
        if s.get('N_ESPERADO') != n:
            falhas.append('CONTAGEM · %s: %d, contrato diz %s' % (nome, n, s.get('N_ESPERADO')))
        conta[dest] += n
        detalhe_sub.append({'NOME': nome, 'DESTINO': dest, 'N': n})

        if dest == 'FORA':
            # FORA nao e um so destino. Uma coisa e ficar fora da grelha e
            # continuar alcancavel pelo cartao que a cita; outra e nao entrar de
            # forma nenhuma. Confundir as duas apaga a camada de evidencia.
            if s.get('CLASSE_DO_FORA') not in ('EVIDENCE_ONLY', 'DROPPED'):
                falhas.append('FORA_SEM_CLASSE · %s nao diz se e EVIDENCE_ONLY ou DROPPED' % nome)
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
    # ⚠️ A PRIMEIRA VERSAO CONFERIA FICHEIROS E NAO COLECCOES, e o inventario V2
    # apanhou-a: um subconjunto declarava SOURCES e o mesmo ficheiro trazia WEB,
    # HANDLES e VIDEO_ROUTES_MEASURED sem dono. Os 96 que escaparam em FONTES, os
    # 86 em FITOSSANITARIO e os 13 em SINAIS_DE_CAMPO eram quase todos
    # inteligencia NEGATIVA — NOT_CROSSED_AND_WHY, REFUTED_AND_WHY,
    # MEASURED_AND_LEFT_OUT, ROUTES_NOT_REACHED_FROM_THIS_SESSION.
    #
    #     RECLAMAR O FICHEIRO E DIZER «ESTE E MEU». RECLAMAR A COLECCAO E DIZER
    #     O QUE SE FAZ COM ELA. SO A SEGUNDA E CONTRATO.
    rx = re.compile(C.get('REGEX_DA_FAMILIA', '$^'), re.I)
    reclamado_fic = {f for f, _ in reclamados}
    orfaos = []
    for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
        for n in sorted(nomes):
            if not n.endswith('.json'):
                continue
            fp = os.path.join(base, n)
            if not rx.search(fp):
                continue
            if not _do_escopo(fp, familia):
                continue
            nf = os.path.normpath(fp)
            try:
                d = json.load(open(fp, encoding='utf-8'))
            except Exception:
                continue
            cols = ([('(raiz e lista)', len(d))] if isinstance(d, list) and d else
                    [(k, len(v)) for k, v in d.items()
                     if isinstance(v, list) and v and isinstance(v[0], dict)]
                    if isinstance(d, dict) else [])
            if not cols and nf not in reclamado_fic:
                orfaos.append('%s · (doc unico)' % os.path.relpath(fp, ROOT))
            for k, cn in cols:
                if (nf, k) not in reclamados and (nf, '(todas as listas)') not in reclamados:
                    orfaos.append('%s · %s (%d)' % (os.path.relpath(fp, ROOT), k, cn))
    exige(not orfaos, 'TODA_COLECCAO_TEM_DONO',
          '%d coleccao(oes) da familia que nenhum subconjunto reclama: %s'
          % (len(orfaos), orfaos[:4]))

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
