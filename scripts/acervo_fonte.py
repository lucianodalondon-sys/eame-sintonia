#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A ESPINHA DA PROVENIÊNCIA — o acervo entra pinado, ou não entra.

    from acervo_fonte import ler, MANIFESTO

O PROBLEMA QUE ISTO RESOLVE
---------------------------
`competitor-activities.json` declara, no cabeçalho, que veio de
`data/samples/META-EAME/META-ADS-ENTITIES-EAME-V1.json`. Esse arquivo **não
existe nesta linhagem**. Ele vive noutro ref. Quem lesse o cabeçalho e fosse
procurar o insumo não o encontraria — e concluiria que a proveniência é falsa,
quando ela só está noutra prateleira.

    UM CAMINHO SEM REF NÃO É ENDEREÇO: É LEMBRANÇA DE ONDE O ARQUIVO ESTAVA.

Aqui todo insumo de acervo é endereçado por **(COMMIT, PATH, BLOB)** e conferido
por **SHA256 do conteúdo**. Três consequências:

    1  o insumo é imutável — commit pinado não se move sozinho;
    2  a integridade é verificável — o SHA256 confere byte a byte;
    3  a pergunta «quais bytes sustentam esta evidência?» tem resposta exata:
       BLOB + o intervalo de caracteres dentro do campo.

E o que NÃO se resolve aqui, não se disfarça: se o blob não abre, a função
levanta erro. Ela nunca devolve um objeto vazio fingindo que o acervo respondeu.

    COLETA QUE FALHA TEM DE FALHAR ALTO. O SILÊNCIO É QUE APAGA ACERVO.
"""
import hashlib
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTO = os.path.join(ROOT, 'data', 'acervo', 'ACERVO-SOURCES-V1.json')


class AcervoIndisponivel(RuntimeError):
    """O insumo pinado não abriu. NÃO é para ser engolido em silêncio."""


def _git(*args):
    p = subprocess.run(['git'] + list(args), cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise AcervoIndisponivel(
            'git ' + ' '.join(args) + ' => ' + p.stderr.decode('utf-8', 'replace')[:300])
    return p.stdout


def manifesto():
    with open(MANIFESTO, encoding='utf-8') as f:
        return json.load(f)


def _por_chave():
    return {s['KEY']: s for s in manifesto()['SOURCES']}


def bytes_de(chave, fontes=None):
    """Os bytes exatos do insumo pinado, conferidos contra o SHA256 declarado."""
    s = (fontes or _por_chave())[chave]
    bruto = _git('cat-file', 'blob', s['BLOB'])
    got = hashlib.sha256(bruto).hexdigest()
    if got != s['SHA256']:
        raise AcervoIndisponivel(
            '%s: SHA256 diverge. declarado=%s lido=%s — o blob mudou debaixo do '
            'manifesto, e nada aqui vai fingir que nao mudou.'
            % (chave, s['SHA256'][:16], got[:16]))
    return bruto


def ler(chave, fontes=None):
    """O insumo pinado, já em JSON. Erra alto se o blob não abrir."""
    return json.loads(bytes_de(chave, fontes).decode('utf-8'))


def por_familia(familia):
    """As chaves de uma família, na ordem do manifesto (determinística)."""
    return [s['KEY'] for s in manifesto()['SOURCES'] if s['FAMILY'] == familia]


def carimbo(chave, fontes=None):
    """O carimbo de proveniência que vai junto de cada registro derivado."""
    s = (fontes or _por_chave())[chave]
    return {
        'ACERVO_KEY': s['KEY'],
        'ACERVO_REF': s['REF'],
        'ACERVO_COMMIT': s['COMMIT'],
        'ACERVO_PATH': s['PATH'],
        'ACERVO_BLOB': s['BLOB'],
        'ACERVO_SHA256': s['SHA256'],
        'ACERVO_BYTES': s['BYTES'],
    }


def sha256_texto(t):
    """O SHA256 do TEXTO — a chave de 'quais bytes sustentam isto'."""
    return hashlib.sha256((t or '').encode('utf-8')).hexdigest()
