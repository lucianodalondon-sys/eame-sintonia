#!/usr/bin/env python3
"""
E-PHY FRANÇA — o registro oficial francês, baixado com prova de que chegou.

    ANSES / E-Phy é a AUTORIDADE regulatória francesa.
    adama.com/france é o que a EMPRESA apresenta.

São perguntas diferentes, com fontes diferentes, e este arquivo só cuida da
primeira. O cruzamento entre as duas é outro passo, e ele nunca é fusão:

    PUBLIC_CATALOG_PRESENCE ≠ REGULATORY_REGISTRATION

Uso:
    python scripts/ephy_fr.py --baixar    # resolve, baixa, confere, extrai
    python scripts/ephy_fr.py --medir     # só mede o que já está em disco

POR QUE ESTE ARQUIVO EXISTE, E NÃO O `ephy.sh`
------------------------------------------------
O `scripts/ephy.sh` chama `python3`. Nesta máquina Windows `python3` é o atalho
da Loja da Microsoft, que não executa nada. Em 2026-08-30 o download "terminou"
e a pasta ficou vazia, e o número que ia entrar no relatório era ZERO REGISTROS
FRANCESES — um número falso que parecia medido.

O `ephy.sh` continua servindo onde `python3` é Python. Aqui a coleta francesa
usa o interpretador que `scripts/runtime_python.py` PROVOU que executa.

O QUE ESTE ARQUIVO SE RECUSA A FAZER
--------------------------------------
Terminar sem conferir. A pós-condição não é enfeite: ela é a diferença entre

    EMPTY_OUTPUT   — não veio nada, e ninguém sabe por quê
    ZERO_RESULTS   — a fonte respondeu, e a resposta foi zero

O primeiro é um defeito. O segundo é um fato. Publicar o primeiro como se fosse
o segundo é como dizer que a França não registra defensivos porque o telefone
caiu antes de alguém atender.

O TAMANHO, ANTES DO LOTE
--------------------------
O data.gouv.fr DECLARA o tamanho de cada recurso. Baixar e comparar com o
declarado é uma conferência de graça — e pega download truncado, que é o modo
de falha silencioso mais comum de todos.
"""
import datetime
import hashlib
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from runtime_python import conferir_saida                        # noqa: E402

SCRIPT_VERSION = 'ephy_fr-v1-2026-08-30'
COUNTRY = 'FR'

# A fonte. O id do dataset é estável; a URL do arquivo muda a cada publicação
# semanal, e por isso é resolvida pela API em vez de ficar fixa aqui.
DATASET_ID = '575e9fac88ee38072a640390'
API = 'https://www.data.gouv.fr/api/1/datasets/%s/' % DATASET_ID
FONTE = {
    'SOURCE_ID': 'FR-T4-001',
    'NAME': 'ANSES — catálogo E-Phy, dados abertos via data.gouv.fr',
    'ROLE': 'REGULATORY_AUTHORITY',
    'COUNTRY': COUNTRY,
    'LICENSE': 'Licence Ouverte (fr-lo)',
    'WHAT_IT_PROVES': ('autorização nacional: número de AMM, titular, substâncias, '
                       'formulação, função, estado, usos autorizados'),
    'WHAT_IT_DOES_NOT_PROVE': ['o que a ADAMA apresenta no catálogo comercial',
                               'disponibilidade comercial', 'preço', 'estoque'],
}

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36')

DESTINO = os.path.join(ROOT, 'data', 'raw', COUNTRY, 'anses-ephy')
MANIFESTO = os.path.join(DESTINO, 'MANIFESTO-EPHY-FR.json')


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def interpretador():
    """Quem executou. Vai no manifesto porque foi o interpretador que falhou antes."""
    return {'EXECUTABLE': sys.executable,
            'VERSION': '%d.%d.%d' % sys.version_info[:3],
            'PREFIX': sys.prefix,
            'PREFIX_HONEST': os.path.exists(os.__file__)}


def _abrir(url, tentativas=4):
    """GET com repetição. Um reset de conexão não é a fonte dizendo não."""
    ultimo = None
    for n in range(tentativas):
        try:
            rq = urllib.request.Request(url, headers={'User-Agent': UA})
            return urllib.request.urlopen(rq, timeout=300)
        except (urllib.error.URLError, ssl.SSLError, TimeoutError) as e:
            ultimo = e
            if n == tentativas - 1:
                break
            import time
            time.sleep(2 ** n)
    raise RuntimeError('a fonte não respondeu depois de %d tentativas: %s'
                       % (tentativas, ultimo))


def resolver():
    """→ o recurso CSV UTF-8 mais recente, com o tamanho que a fonte DECLARA.

    Escolher por `format == 'zip' and 'utf8' in title` e não por posição na
    lista: a ordem dos recursos não é contrato, e pegar `resources[1]` funciona
    até o dia em que a ANSES publica na outra ordem — e aí baixa o windows-1252
    sem ninguém perceber, e todo acento francês vira lixo.
    """
    with _abrir(API) as r:
        d = json.load(r)
    candidatos = [x for x in d['resources']
                  if (x.get('format') or '').lower() == 'zip'
                  and 'utf8' in (x.get('title') or '').lower()]
    if not candidatos:
        raise RuntimeError('nenhum recurso ZIP UTF-8 no dataset — a fonte mudou de forma')
    if len(candidatos) > 1:
        raise RuntimeError('mais de um recurso ZIP UTF-8 (%d). Escolher no escuro '
                           'seria adivinhar qual é o certo' % len(candidatos))
    r = candidatos[0]
    return {
        'RESOURCE_TITLE': r.get('title'),
        'URL': r.get('url'),
        'DECLARED_BYTES': r.get('filesize'),
        'DECLARED_SHA1': (r.get('checksum') or {}).get('value'),
        'DATASET_LAST_UPDATE': d.get('last_update'),
        'DATASET_TITLE': d.get('title'),
        'LICENSE': d.get('license'),
        'ORGANIZATION': (d.get('organization') or {}).get('name'),
        'RESOURCES_SEEN': [{'format': x.get('format'), 'title': x.get('title'),
                            'filesize': x.get('filesize')} for x in d['resources']],
    }


def baixar():
    """Baixa, confere contra o tamanho declarado, extrai e mede. Nesta ordem."""
    os.makedirs(DESTINO, exist_ok=True)

    # ANTES: o que se vai pedir, e quem está pedindo.
    antes = {'SOURCE': FONTE, 'QUERY': API, 'CAPTURE_TIME': agora(),
             'INTERPRETER': interpretador(), 'SCRIPT_VERSION': SCRIPT_VERSION}
    print('resolvendo o recurso na fonte...')
    alvo = resolver()
    antes['RESOLVED'] = alvo
    print('  recurso   :', alvo['RESOURCE_TITLE'])
    print('  declarado :', alvo['DECLARED_BYTES'], 'bytes')

    zip_local = os.path.join(DESTINO, os.path.basename(alvo['URL'].split('?')[0]))
    if not zip_local.lower().endswith('.zip'):
        zip_local = os.path.join(DESTINO, 'ephy-utf8.zip')

    print('baixando...')
    h = hashlib.sha256()
    n = 0
    with _abrir(alvo['URL']) as r, open(zip_local, 'wb') as fh:
        while True:
            bloco = r.read(1 << 20)
            if not bloco:
                break
            fh.write(bloco)
            h.update(bloco)
            n += len(bloco)
    sha = h.hexdigest()
    print('  recebido  :', n, 'bytes · sha256', sha[:16] + '...')

    # A conferência de graça: o que a fonte declarou contra o que chegou.
    declarado = alvo['DECLARED_BYTES']
    bate = (declarado is None) or (int(declarado) == n)
    if not bate:
        raise RuntimeError('download truncado: a fonte declarou %s bytes e '
                           'chegaram %d' % (declarado, n))

    print('extraindo...')
    extraidos = []
    with zipfile.ZipFile(zip_local) as z:
        for nome in z.namelist():
            if nome.endswith('/'):
                continue
            # Nome de dentro do zip nunca vira caminho de disco sem checagem:
            # um `../` no zip escreveria fora do destino.
            seguro = os.path.basename(nome)
            destino = os.path.join(DESTINO, seguro)
            with z.open(nome) as origem, open(destino, 'wb') as saida:
                saida.write(origem.read())
            extraidos.append(destino)

    depois = medir(extraidos)
    manifesto = dict(antes)
    manifesto.update({
        'ZIP_LOCAL': os.path.relpath(zip_local, ROOT),
        'ZIP_BYTES': n,
        'ZIP_SHA256': sha,
        'DECLARED_BYTES_MATCH': bate,
        'EXTRACTED': depois['FILES'],
        'RECORD_COUNT': depois['RECORD_COUNT'],
        'POSTCONDITION': depois['POSTCONDITION'],
    })
    with open(MANIFESTO, 'w', encoding='utf-8') as fh:
        json.dump(manifesto, fh, ensure_ascii=False, indent=1)
    return manifesto


_LINHA = re.compile(r'[^\r\n]')


def _contar_linhas(caminho):
    """Linhas de dado: total menos o cabeçalho. Sem carregar o arquivo na memória."""
    n = 0
    with open(caminho, 'rb') as fh:
        for _ in fh:
            n += 1
    return max(0, n - 1)


def medir(arquivos=None):
    """Mede o que está em disco. É esta função que decide se a coleta valeu."""
    if arquivos is None:
        arquivos = [os.path.join(DESTINO, x) for x in sorted(os.listdir(DESTINO))
                    if x.lower().endswith('.csv')] if os.path.isdir(DESTINO) else []
    csvs = [a for a in arquivos if a.lower().endswith('.csv')]
    detalhe = []
    total = 0
    for a in csvs:
        linhas = _contar_linhas(a)
        total += linhas
        detalhe.append({'FILE': os.path.basename(a),
                        'BYTES': os.path.getsize(a),
                        'ROWS': linhas,
                        'SHA256': _sha(a)})
    pos = conferir_saida(caminhos=csvs, exit_code=0, contagem=total,
                         contagem_minima=1)
    return {'FILES': detalhe, 'RECORD_COUNT': total, 'POSTCONDITION': pos}


def _sha(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else '--medir'
    if modo == '--baixar':
        m = baixar()
        print()
        print('SOURCE          :', m['SOURCE']['NAME'])
        print('DATASET UPDATE  :', m['RESOLVED']['DATASET_LAST_UPDATE'])
        print('ZIP BYTES       :', m['ZIP_BYTES'])
        print('ZIP SHA256      :', m['ZIP_SHA256'])
        print('ARQUIVOS        :', len(m['EXTRACTED']))
        print('RECORD_COUNT    :', m['RECORD_COUNT'])
        print('POS-CONDICAO    :', m['POSTCONDITION']['STATE'])
        return 0 if m['POSTCONDITION']['STATE'] == 'OUTPUT_OK' else 1
    m = medir()
    for f in m['FILES']:
        print('%9d linhas  %10d bytes  %s' % (f['ROWS'], f['BYTES'], f['FILE']))
    print('RECORD_COUNT :', m['RECORD_COUNT'])
    print('POS-CONDICAO :', m['POSTCONDITION']['STATE'], '—', m['POSTCONDITION']['WHY'])
    return 0 if m['POSTCONDITION']['STATE'] == 'OUTPUT_OK' else 1


if __name__ == '__main__':
    sys.exit(main())
