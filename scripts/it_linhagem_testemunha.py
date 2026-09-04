#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A TESTEMUNHA DA LINHAGEM — provar ancestralidade num clone que nao a tem.

    python3 scripts/it_linhagem_testemunha.py <ancestral> <descendente>

POR QUE ESTE FICHEIRO EXISTE
----------------------------
Um clone `--single-branch` da Linha B nao tem 8c082f7 nem 0b490ec: sao commits
de outra linhagem, e o handoff so os NOMEIA. O portao do lote pergunta se os
carimbos estao na mesma historia, nao consegue responder, e cai para 11/12.

    RESPONDER COM `git fetch --all` SERIA TROCAR UMA PROVA POR UMA LIGACAO.

O que se versiona aqui e a coisa mais pequena que ainda prova: o CORPO CRU de
cada commit da cadeia. Com ele, qualquer maquina offline refaz o que o Git faz —
sha1("commit " + tamanho + "\\0" + corpo) — e obtem o SHA de volta. Se um byte
mudar, o SHA muda. Se um `parent` mudar, a cadeia parte-se. Nao ha nada a
confiar: ha uma conta a repetir.

    UMA TESTEMUNHA QUE PEDE CONFIANCA NAO E TESTEMUNHA. E UM RECADO.

O que ela NAO faz: nao prova que o conteudo das arvores e o mesmo, e nao
substitui o Git quando o Git tem os objectos. E o segundo melhor, usado so
quando o primeiro nao existe.
"""
import base64
import hashlib
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'italia-portale', 'audit', 'UPSTREAM-LINEAGE-WITNESS.json')


def git(*a):
    r = subprocess.run(['git'] + list(a), cwd=ROOT, capture_output=True)
    if r.returncode:
        raise SystemExit('git %s falhou: %s' % (' '.join(a), r.stderr.decode()[:200]))
    return r.stdout


def corpo(sha):
    return git('cat-file', 'commit', sha)


def sha_do_corpo(b):
    return hashlib.sha1(b'commit %d\0' % len(b) + b).hexdigest()


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    ancestral = git('rev-parse', sys.argv[1]).decode().strip()
    descendente = git('rev-parse', sys.argv[2]).decode().strip()

    # a cadeia, do descendente para tras, ate ao ancestral inclusive
    saltos = git('rev-list', '--ancestry-path', '%s..%s' % (ancestral, descendente)).decode().split()
    cadeia = saltos + [ancestral]

    commits = []
    for sha in cadeia:
        b = corpo(sha)
        conferido = sha_do_corpo(b)
        if conferido != sha:
            raise SystemExit('o corpo de %s nao reproduz o seu SHA (deu %s)' % (sha, conferido))
        pais = [l.split()[1] for l in b.decode('utf-8', 'replace').split('\n')
                if l.startswith('parent ')]
        commits.append({
            'SHA': sha,
            'PARENTS': pais,
            'ASSUNTO': b.decode('utf-8', 'replace').split('\n\n', 1)[-1].split('\n')[0][:110],
            'CORPO_B64': base64.b64encode(b).decode('ascii'),
        })

    doc = {
        'DATASET': 'SINTONIA-UPSTREAM-LINEAGE-WITNESS-V1',
        'LAYER': 'PROVA DE LINHAGEM — offline, verificavel pelas regras do proprio Git',
        'COUNTRY': 'IT',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'git cat-file commit, para cada commit entre ANCESTOR e DESCENDANT inclusive',
        'LEI': ('um clone single-branch da Linha B nao tem estes commits. Esta testemunha permite '
                'provar a ancestralidade sem rede: recalcula-se sha1("commit "+len+NUL+corpo) e '
                'segue-se a cadeia de parent. Se um byte, um parent ou um SHA mudar, falha.'),
        'ANCESTOR': ancestral,
        'DESCENDANT': descendente,
        'COMMITS': commits,
        'COMO_VERIFICAR': ('para cada COMMITS[i]: sha1("commit "+len(corpo)+"\\0"+corpo) == SHA; '
                          'depois seguir PARENTS de DESCENDANT ate ANCESTOR sem saltos.'),
        'O_QUE_NAO_PROVA': ('nao prova o conteudo das arvores nem que o remoto ainda tem estes '
                            'commits. Prova que a cadeia declarada existe e nao foi tocada.'),
        'PRECEDENCIA': 'quando o Git local TEM os objectos, e o Git que responde. Isto e o segundo melhor.',
    }
    with io.open(SAIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    print('  escrito : %s' % os.path.relpath(SAIDA, ROOT))
    print('  cadeia  : %s' % ' -> '.join(c['SHA'][:7] for c in reversed(commits)))
    print('  bytes   : %d' % os.path.getsize(SAIDA))


if __name__ == '__main__':
    main()
