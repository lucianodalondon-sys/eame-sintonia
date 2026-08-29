#!/usr/bin/env python3
"""
AUDITORIA CONTRA ALVO CONGELADO — impede o defeito de método da auditoria anterior.

O que aconteceu em 2026-08-29: a auditoria correu contra o branch enquanto oito commits
entravam. Um auditor afirmou que a regra não existia em `docs/regras/` e listou 4 arquivos
onde havia 5, porque leu antes do commit que a criou. A verificação pegou o caso, mas o
desenho estava errado.

A regra que passa a valer:

    AUDIT_TARGET_SHA é definido ANTES. Se a árvore auditada não corresponder a ele,
    a auditoria é INVÁLIDA — não "com ressalva", inválida.

`congelar()` cria um snapshot só-leitura via `git worktree` num SHA fixo. O auditor lê o
snapshot; o branch pode receber commits à vontade sem contaminar nada.
"""
import datetime
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CAMPOS_AUDITORIA = [
    'AUDIT_ID', 'AUDIT_TARGET_SHA', 'AUDIT_STARTED_AT', 'AUDIT_FINISHED_AT',
    'AUDITOR_VERSION', 'SCRIPT_VERSION', 'SNAPSHOT_PATH', 'VALID', 'INVALID_REASON',
]

# Versão do próprio auditor. Muda quando o método muda, para que duas auditorias com
# resultados diferentes possam ser comparadas sabendo se o método era o mesmo.
SCRIPT_VERSION = 'auditoria.py/1.0.0'


def agora():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _git(*args, cwd=ROOT):
    r = subprocess.run(['git'] + list(args), cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('git %s falhou: %s' % (' '.join(args), r.stderr.strip()[:200]))
    return r.stdout.strip()


def sha_atual():
    return _git('rev-parse', 'HEAD')


def arvore_limpa():
    return _git('status', '--porcelain') == ''


def congelar(sha, destino=None):
    """Cria um worktree só-leitura no SHA dado. Devolve o caminho do snapshot.

    O snapshot é `--detach`: não é um branch e não pode receber commit por acidente.
    """
    destino = destino or os.path.join('/tmp', 'audit-snapshot-%s' % sha[:12])
    if os.path.exists(destino):
        return destino
    _git('worktree', 'add', '--detach', destino, sha)
    return destino


def descongelar(destino):
    try:
        _git('worktree', 'remove', '--force', destino)
    except RuntimeError:
        pass


def validar(registro, snapshot=None):
    """A auditoria só vale se o alvo não se mexeu.

    Duas checagens independentes:
      1. o snapshot está exatamente no SHA declarado;
      2. o snapshot não tem alteração não commitada.
    """
    sha = registro.get('AUDIT_TARGET_SHA')
    if not sha:
        return False, 'AUDIT_TARGET_SHA não foi definido antes da auditoria'
    caminho = snapshot or registro.get('SNAPSHOT_PATH')
    if not caminho or not os.path.isdir(caminho):
        return False, 'snapshot inexistente: a auditoria leu uma árvore que não foi congelada'
    real = _git('rev-parse', 'HEAD', cwd=caminho)
    if real != sha:
        return False, 'o SHA auditado mudou: declarado %s, encontrado %s' % (sha[:12], real[:12])
    if _git('status', '--porcelain', cwd=caminho) != '':
        return False, 'a árvore auditada tem alteração não commitada — o alvo não estava congelado'
    return True, ''


def abrir(audit_id, sha=None):
    """Abre uma auditoria: congela o alvo e devolve o registro já iniciado."""
    sha = sha or sha_atual()
    snapshot = congelar(sha)
    return {
        'AUDIT_ID': audit_id,
        'AUDIT_TARGET_SHA': sha,
        'AUDIT_STARTED_AT': agora(),
        'AUDIT_FINISHED_AT': None,
        'AUDITOR_VERSION': os.environ.get('AUDITOR_VERSION', 'NÃO SEI'),
        'SCRIPT_VERSION': SCRIPT_VERSION,
        'SNAPSHOT_PATH': snapshot,
        'VALID': None,
        'INVALID_REASON': None,
    }


def fechar(registro):
    """Fecha e valida. `VALID=False` significa auditoria descartada, não relativizada."""
    registro['AUDIT_FINISHED_AT'] = agora()
    ok, motivo = validar(registro)
    registro['VALID'] = ok
    registro['INVALID_REASON'] = motivo or None
    return registro


if __name__ == '__main__':
    import sys
    if '--congelar' in sys.argv:
        sha = sha_atual()
        print('SHA:', sha)
        print('árvore limpa:', arvore_limpa())
        print('snapshot:', congelar(sha))
    else:
        print('SCRIPT_VERSION :', SCRIPT_VERSION)
        print('HEAD           :', sha_atual())
        print('árvore limpa   :', arvore_limpa())
        print('campos         :', ', '.join(CAMPOS_AUDITORIA))
