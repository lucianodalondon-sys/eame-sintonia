#!/usr/bin/env python3
"""
RAW ITALIANO — o plano de preservação nasce com o primeiro asset, não depois.

A Espanha fez a preservação RAW virar frente posterior, e pagou por isso: o gate
só apareceu quando já havia muito documento baixado e nenhum jeito barato de
provar que os bytes remotos eram os certos.

Na Itália o plano vem antes de existir um único arquivo. Este módulo não baixa
nada — ele define o que baixar significa, e o que fecha o portão.

O PIPELINE, E CADA SETA É UM ESTADO
-------------------------------------
    DOWNLOAD → LOCAL SHA256 → METADATA → RAW PLAN → STORAGE KEY
             → UPLOAD → REMOTE INVENTORY → DOWNLOAD BACK → SHA VERIFY

A ÚLTIMA SETA É A QUE IMPORTA
-------------------------------
"O objeto existe no bucket" e "o objeto tem os bytes que eu enviei" são
afirmações diferentes, e só a segunda serve. Um upload truncado, um retry que
gravou por cima, um arquivo com o nome certo e o conteúdo de outro — todos
passam por REMOTE_PRESENT e nenhum passa por CONTENT_HASH_VERIFIED.

    RAW PRESENCE ≠ RAW CONTENT VERIFIED

E O 5XX
--------
    HTTP_5XX ≠ OBJECT_NOT_PRESERVED

Uma resposta ambígua não diz que o objeto não foi gravado — diz que não se sabe.
Reenviar às cegas depois de um 5xx pode duplicar ou corromper. A ordem é
inventário remoto, depois download e hash, e só então um estado.
"""
import hashlib
import os

# Estados do objeto individual.
LOCAL_ONLY = 'LOCAL_ONLY'
UPLOADED_UNVERIFIED = 'UPLOADED_NOT_VERIFIED'
REMOTE_PRESENT = 'REMOTE_PRESENT'
CONTENT_HASH_VERIFIED = 'CONTENT_HASH_VERIFIED'
HASH_MISMATCH = 'HASH_MISMATCH'
REMOTE_ABSENT = 'REMOTE_ABSENT'
ORPHAN = 'ORPHAN'                 # existe no remoto e ninguém o esperava
FAILED = 'FAILED'
UNKNOWN_MUST_VERIFY = 'UNKNOWN_MUST_VERIFY'

# Limite a MEDIR antes do lote, nunca a descobrir no fim. A Espanha provou que
# "o bucket não declara limite" não é o mesmo que "não há limite".
LIMITE_A_MEDIR = {
    'WHAT': 'o maior asset italiano, em bytes, antes de abrir lote',
    'WHY': ('bucket sem limite específico não significa ausência de limite '
            'global — e descobrir isso no último arquivo custa o lote inteiro'),
    'IF_EXCEEDED': 'tratar explicitamente com upload multipart ou recorte declarado',
    'STATE': 'NOT_MEASURED — nenhum asset italiano baixado ainda',
}


def sha256_arquivo(caminho, bloco=1 << 20):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for b in iter(lambda: f.read(bloco), b''):
            h.update(b)
    return h.hexdigest()


def plano_raw(url, storage_key, sha_local, bytes_, content_type, produto=None):
    """O plano de um objeto. Nasce junto com o download, não depois dele."""
    return {
        'URL': url, 'STORAGE_KEY': storage_key,
        'SHA256_LOCAL': sha_local, 'BYTES': bytes_, 'CONTENT_TYPE': content_type,
        'RELATED_PRODUCT': produto,
        'STATE': LOCAL_ONLY,
        'SHA256_REMOTE': None,
        'COUNTRY': 'IT',
    }


def apos_resposta_ambigua(http_status):
    """O que fazer depois de um 5xx. Nunca reenviar às cegas.

    Devolve estado e o PRÓXIMO passo, porque a decisão errada aqui é agir — e a
    certa é olhar antes.
    """
    if 500 <= int(http_status) < 600:
        return {'STATE': UNKNOWN_MUST_VERIFY,
                'NEXT': 'remote inventory, depois download back e hash',
                'DO_NOT': 'reenviar às cegas',
                'WHY': 'HTTP_5XX ≠ OBJECT_NOT_PRESERVED'}
    return {'STATE': FAILED, 'NEXT': 'registrar e seguir',
            'WHY': 'resposta não ambígua'}


def verificar(plano, sha_remoto):
    """Compara o hash do que voltou com o do que subiu. É aqui que o RAW fecha."""
    p = dict(plano)
    if sha_remoto is None:
        p['STATE'] = REMOTE_ABSENT
        return p
    p['SHA256_REMOTE'] = sha_remoto
    p['STATE'] = (CONTENT_HASH_VERIFIED if sha_remoto == plano['SHA256_LOCAL']
                  else HASH_MISMATCH)
    return p


def gate(*, esperado, remoto_presente, remoto_ausente, orfaos, falhos,
         hash_conferido, hash_divergente):
    """O portão RAW italiano. Fecha com sete condições, e a sétima é a que conta.

    Aceitar "N objetos existem" fecharia com um bucket cheio de bytes errados.
    """
    condicoes = {
        'EXPECTED_EQ_REMOTE_PRESENT': remoto_presente == esperado,
        'REMOTE_ABSENT_ZERO': remoto_ausente == 0,
        'ORPHANS_ZERO': orfaos == 0,
        'FAILED_ZERO': falhos == 0,
        'CONTENT_HASH_CHECKED_EQ_EXPECTED': hash_conferido == esperado,
        'HASH_MISMATCH_ZERO': hash_divergente == 0,
        'EXPECTED_POSITIVE': esperado > 0,
    }
    faltam = sorted(k for k, v in condicoes.items() if not v)
    return {
        'STATE': 'CLOSED' if not faltam else 'OPEN',
        'EXPECTED': esperado, 'REMOTE_PRESENT': remoto_presente,
        'REMOTE_ABSENT': remoto_ausente, 'ORPHANS': orfaos, 'FAILED': falhos,
        'CONTENT_HASH_CHECKED': hash_conferido, 'HASH_MISMATCH': hash_divergente,
        'CONDITIONS': condicoes,
        'MISSING': faltam,
        'WHY': ('todas as sete condições satisfeitas' if not faltam
                else 'faltam: ' + ', '.join(faltam)),
    }


if __name__ == '__main__':
    print('estados:', LOCAL_ONLY, REMOTE_PRESENT, CONTENT_HASH_VERIFIED)
    print('limite a medir:', LIMITE_A_MEDIR['STATE'])
    print('gate so com presenca :', gate(esperado=3, remoto_presente=3,
                                         remoto_ausente=0, orfaos=0, falhos=0,
                                         hash_conferido=0, hash_divergente=0)['STATE'])
    print('gate com hash        :', gate(esperado=3, remoto_presente=3,
                                         remoto_ausente=0, orfaos=0, falhos=0,
                                         hash_conferido=3, hash_divergente=0)['STATE'])
