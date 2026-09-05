#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O HANDOFF DE UMA FAMILIA — o que a Linha B recebe, e nada mais.

    python3 scripts/it_familia_handoff.py FONTES [--source-head <sha>]
    python3 scripts/it_familia_handoff.py --todas --source-head <sha>

Mesma lei do handoff do Radar Futuro: NAO recalcula julgamento, NAO reclassifica,
NAO cria QA, NAO altera CLIENT_SAFE. So empacota decisoes que o contrato ja
aprovou, e carimba os hashes do que leu para o receptor poder provar que recebeu
o mesmo.

    UM HANDOFF QUE OBRIGA O RECEPTOR A RECALCULAR NAO E HANDOFF:
    E O TRABALHO OUTRA VEZ, COM OUTRO DONO.

FORA nao e um so destino: EVIDENCE_ONLY continua alcancavel pelo cartao que o
cita; DROPPED nao entra de forma nenhuma. O handoff separa-os porque juntar os
dois apagaria a camada de evidencia com o mesmo gesto que limpa o ruido.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(ROOT, 'data', 'samples')
DIR = os.path.join(SAMPLES, 'IT-PORTAL-V1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from it_acervo_inventario_v2 import (familia as _fam, e_italiano as _it,  # noqa: E402
                                     coleccoes as _cols)


def _sha(p):
    with open(p, 'rb') as f:
        return 'sha256:' + hashlib.sha256(f.read()).hexdigest()[:32]


def cabeca(argv):
    if '--source-head' in argv:
        return argv[argv.index('--source-head') + 1]
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def _regs(doc, chave):
    if chave == '(doc unico)':
        return [doc]
    if chave == '(todas as listas)':
        fora = []
        for v in doc.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                fora.extend(v)
        return fora or [doc]
    v = doc.get(chave) if isinstance(doc, dict) else None
    return v if isinstance(v, list) else []


def um(fam, head):
    C = json.load(open(os.path.join(DIR, 'IT-CONTRATO-FAMILIA-%s-V1.json' % fam),
                       encoding='utf-8'))
    conta = {'CARTAO': 0, 'COM_METODO': 0, 'EVIDENCE_ONLY': 0, 'DROPPED': 0}
    entradas, hashes, nao_sei, avisos, campos, limites, exclusoes = [], {}, 0, {}, {}, [], []

    for s in C['SUBCONJUNTOS']:
        dest, nome = s['DESTINO'], s['NOME']
        alvo = dest if dest != 'FORA' else s['CLASSE_DO_FORA']
        # os ficheiros deste subconjunto, no mesmo recorte do inventario
        fics = []
        if s.get('PADRAO'):
            prx = re.compile(s['PADRAO'], re.I)
            for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
                for n in sorted(nomes):
                    q = os.path.join(base, n)
                    if not n.endswith('.json') or not prx.search(q):
                        continue
                    rel = os.path.relpath(q, ROOT)
                    try:
                        d = json.load(open(q, encoding='utf-8'))
                    except Exception:
                        continue
                    if _it(rel, d) and _fam(rel) == fam:
                        fics.append(q)
        else:
            fics = [os.path.join(SAMPLES, s['FICHEIRO'])]

        n_sub = 0
        for q in fics:
            hashes[os.path.relpath(q, ROOT)] = _sha(q)
            regs = _regs(json.load(open(q, encoding='utf-8')), s['CHAVE_DA_LISTA'])
            n_sub += len(regs)
            if alvo in ('EVIDENCE_ONLY', 'DROPPED'):
                continue
            chave_id = s.get('CHAVE_DE_ID')
            for i, r in enumerate(regs):
                ident = (r.get(chave_id) if chave_id and isinstance(r, dict)
                         else '%s#%d' % (nome.replace(' ', '_'), i))
                lim = {}
                ns = (s.get('NAO_SEI') or {}).get('CAMPO')
                if ns and isinstance(r, dict):
                    v = r.get(ns)
                    if v in (None, '', 'NAO_SEI', 'UNKNOWN') or \
                       (isinstance(v, str) and v.strip().upper().startswith(('NAO_SEI', 'NAO SEI', 'UNKNOWN'))):
                        nao_sei += 1
                        lim['NAO_SEI'] = {'CAMPO': ns, 'VALOR': v}
                entradas.append({'ID': ident, 'SUBCONJUNTO': nome, 'DESTINO': alvo,
                                 'AVISO': s.get('AVISO'), 'LIMITES': lim or None})
        conta[alvo] += n_sub

        if alvo in ('CARTAO', 'COM_METODO'):
            campos[nome] = s.get('CAMPOS_MINIMOS')
            if s.get('AVISO'):
                avisos[nome] = s['AVISO']
            limites.append({'SUBCONJUNTO': nome, 'NAO_SEI': s.get('NAO_SEI'),
                            'REMOVE_INTERNOS': bool(s.get('REMOVE_INTERNOS'))})
        else:
            exclusoes.append({'SUBCONJUNTO': nome, 'CLASSE': alvo, 'N': n_sub,
                              'RAZAO': s['PORQUE']})

    return {
        'DATASET': 'IT-HANDOFF-LINHA-B-%s-V1' % fam,
        'LEI': 'empacota o que o contrato ja aprovou. Nao recalcula julgamento, nao '
               'reclassifica, nao cria QA e nao altera CLIENT_SAFE.',
        'UPSTREAM_CHECKPOINT': head,
        'SOURCE_HEAD': head,
        'CONTRACT_VERSION': C['DATASET'],
        'COLLECTION': fam,
        'DONO_DA_DECISAO': C['DONO_DA_DECISAO'],
        'TOTAL': sum(conta.values()),
        'RENDERABLE_CARD': conta['CARTAO'],
        'RENDERABLE_WITH_METHOD': conta['COM_METODO'],
        'EVIDENCE_ONLY': conta['EVIDENCE_ONLY'],
        'DROPPED': conta['DROPPED'],
        'NAO_SEI': nao_sei,
        'LEI_DA_FAMILIA': C['LEI'],
        'PROVENIENCIA': {'SOURCE_ARTIFACT_HASHES': hashes,
                         'ACHADO_DA_CONTAGEM': C.get('ACHADO_DA_CONTAGEM')},
        'CAMPOS_OBRIGATORIOS': campos,
        'AVISOS_OBRIGATORIOS': avisos,
        'LIMITES': limites,
        'CAMPOS_QUE_NUNCA_ATRAVESSAM': C.get('CAMPOS_QUE_NUNCA_ATRAVESSAM'),
        'RAZAO_DE_EXCLUSAO': exclusoes,
        'ENTRADAS_AUTORIZADAS': entradas,
    }


def main():
    head = cabeca(sys.argv)
    argv = [a for a in sys.argv[1:] if not a.startswith('--')
            and a != head]
    fams = argv or ['SINAIS_DE_CAMPO', 'FONTES', 'FITOSSANITARIO']
    print('== HANDOFFS POR FAMILIA -> LINHA B ==')
    print('  %-18s %6s %7s %9s %9s %8s %8s' % ('FAMILIA', 'TOTAL', 'CARTAO',
                                               'C/METODO', 'EVIDENCE', 'DROPPED', 'NAO_SEI'))
    for fam in fams:
        d = um(fam, head)
        p = os.path.join(DIR, 'IT-HANDOFF-LINHA-B-%s-V1.json' % fam)
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  %-18s %6d %7d %9d %9d %8d %8d'
              % (fam, d['TOTAL'], d['RENDERABLE_CARD'], d['RENDERABLE_WITH_METHOD'],
                 d['EVIDENCE_ONLY'], d['DROPPED'], d['NAO_SEI']))
        print('       entradas autorizadas %d · artefactos com hash %d'
              % (len(d['ENTRADAS_AUTORIZADAS']), len(d['PROVENIENCIA']['SOURCE_ARTIFACT_HASHES'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
