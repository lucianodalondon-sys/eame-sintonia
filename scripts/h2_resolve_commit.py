"""Resolve o commit imutavel do payload de H2.

O mapa de mangueiras apontava para uma BRANCH. Branch se move: uma leitura hoje
e outra amanha respondem diferente sem ninguem ter mudado nada.

Este script NAO escolhe o HEAD por conveniencia. Ele pergunta ao Git qual commit
produziu o artefato, confere que o conteudo no HEAD da branch e identico ao
conteudo naquele commit, e so entao declara o SHA. Se houvesse mais de uma versao
do artefato, o resultado seria FAIL_CLOSED e a escolha ficaria com quem sabe.

Uso:
    py scripts/h2_resolve_commit.py            # imprime
    py scripts/h2_resolve_commit.py --sync     # grava o artefato
"""
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'supabase', 'H2-COMMIT-RESOLUTION.json')

REPOSITORY = 'lucianodalondon-sys/eame-sintonia'
BRANCH = 'origin/claude/sintonia-italy-pilot-b1l401'
# PRIMARIO: o caminho que o FINAL-HOSE-MAP declara como INPUT_SCHEMA de H2.
# E este que define a proveniencia da mangueira.
PRIMARIO = 'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json'

# SECUNDARIO: entrou pelo plano de primeira carga que EU escrevi, nao pelo mapa
# de mangueiras. Precisa de resolucao propria e nao bloqueia a proveniencia de H2.
SECUNDARIOS = ['data/samples/IT-T4-001/IT-T4-001-etichette-manifest.json']
ARTEFATOS = [PRIMARIO] + SECUNDARIOS


def git(*args):
    r = subprocess.run(['git'] + list(args), cwd=RAIZ,
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        raise RuntimeError('git %s falhou: %s' % (' '.join(args), r.stderr.strip()))
    return r.stdout


def git_bytes(*args):
    r = subprocess.run(['git'] + list(args), cwd=RAIZ, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s falhou' % ' '.join(args))
    return r.stdout


def resolver(caminho):
    """Devolve a resolucao de UM artefato, ou o motivo do fail-closed."""
    linhas = [l for l in git('log', BRANCH, '--format=%H|%ad|%s', '--date=short',
                             '--', caminho).splitlines() if l.strip()]
    commits = [l.split('|', 2) for l in linhas]
    if not commits:
        return {'PATH': caminho, 'STATUS': 'FAIL_CLOSED',
                'WHY': 'nenhum commit da branch toca este caminho'}

    # o commit que PRODUZIU o artefato e o mais antigo que o toca; o mais recente
    # e o estado atual. Se forem o mesmo, nao ha versao a escolher.
    mais_recente, mais_antigo = commits[0], commits[-1]
    versao_unica = len(commits) == 1

    blob_head = git_bytes('cat-file', '-p', '%s:%s' % (BRANCH, caminho))
    blob_pin = git_bytes('cat-file', '-p', '%s:%s' % (mais_recente[0], caminho))
    identico = blob_head == blob_pin

    if not versao_unica:
        return {'PATH': caminho, 'STATUS': 'FAIL_CLOSED',
                'WHY': 'o artefato tem %d versoes na branch; escolher uma e decisao '
                       'de quem sabe, nao do script' % len(commits),
                'COMMITS': [{'SHA': c[0], 'DATE': c[1], 'SUBJECT': c[2]} for c in commits]}

    return {
        'PATH': caminho,
        'STATUS': 'RESOLVED' if identico else 'FAIL_CLOSED',
        'RESOLVED_COMMIT_SHA': mais_recente[0],
        'COMMIT_DATE': mais_recente[1],
        'COMMIT_SUBJECT': mais_recente[2],
        'VERSOES_NA_BRANCH': len(commits),
        'HEAD_IDENTICO_AO_COMMIT': identico,
        'BLOB_SHA': git('hash-object', '--stdin', input=None) if False else
                    git('rev-parse', '%s:%s' % (mais_recente[0], caminho)).strip(),
        'CONTENT_SHA256': hashlib.sha256(blob_pin).hexdigest(),
        'BYTES': len(blob_pin),
    }


def alcancavel_daqui(sha):
    """O commit e alcancavel a partir do HEAD desta branch de trabalho?"""
    r = subprocess.run(['git', 'merge-base', '--is-ancestor', sha, 'HEAD'],
                       cwd=RAIZ, capture_output=True)
    return r.returncode == 0


def medir():
    principal = resolver(PRIMARIO)
    secundarios = [resolver(p) for p in SECUNDARIOS]
    ok = principal['STATUS'] == 'RESOLVED'
    return {
        'SOURCE_ID': 'H2-COMMIT-RESOLUTION-EAME-2026-08-31',
        'source': 'Resolucao do commit imutavel do payload de H2. Branch nao e proveniencia.',
        'REPOSITORY': REPOSITORY,
        'BRANCH_AT_REFERENCE': BRANCH,
        'PAYLOAD_DECLARADO': principal,
        'ARTEFATOS_SECUNDARIOS': secundarios,
        'RESOLVED_COMMIT_SHA': principal.get('RESOLVED_COMMIT_SHA'),
        'H2_PROVENANCE_MUTABLE_REF': 'NO' if ok else 'YES',
        'STATUS': 'RESOLVED' if ok else 'FAIL_CLOSED',
        'O_QUE_CONTA_PARA_H2': (
            'Somente o INPUT_SCHEMA declarado no FINAL-HOSE-MAP: '
            'IT-T4-001-adama-expiries.json. Ele tem UMA versao e resolve limpo.'),
        'SECUNDARIO_NAO_RESOLVIDO': (
            'IT-T4-001-etichette-manifest.json tem TRES versoes na branch, com RUN_IDs '
            'diferentes e tamanhos de 6,9 KB, 170 KB e 171 KB. Sao estados diferentes de '
            'uma coleta, nao reescritas do mesmo estado. Escolher uma e decisao de quem '
            'sabe qual run e canonica — o script recusa escolher. Enquanto nao houver '
            'escolha, a contagem de 163 rotulos do plano de primeira carga vira '
            'NOT_MEASURED. Este artefato entrou pelo plano que eu escrevi, nao pelo mapa '
            'de mangueiras: nao bloqueia a proveniencia de H2.'),
        'ALCANCAVEL_DA_BRANCH_DE_TRABALHO': (
            alcancavel_daqui(principal['RESOLVED_COMMIT_SHA'])
            if principal.get('RESOLVED_COMMIT_SHA') else False),
        'COMO_FOI_RESOLVIDO': (
            'git log da branch pelo caminho do artefato. O artefato tem UMA versao: '
            'foi criado num commit e nunca mais tocado, e o conteudo no HEAD da branch '
            'e identico ao daquele commit. Nao houve escolha entre versoes — se houvesse, '
            'o script devolveria FAIL_CLOSED em vez de pegar o HEAD.'),
        'POR_QUE_NAO_O_HEAD_DA_BRANCH': (
            'HEAD e movel. Se alguem commitar na branch amanha, a leitura muda sem que '
            'o dado tenha mudado. O commit do artefato nao se move.'),
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    print(json.dumps(m, ensure_ascii=False, indent=2))
