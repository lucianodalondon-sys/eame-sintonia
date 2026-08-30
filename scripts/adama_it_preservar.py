#!/usr/bin/env python3
"""
PRESERVAÇÃO DOS BYTES ITALIANOS — disco local → Supabase Storage, com prova.

O acervo de `data/raw/IT/adama-website/` existe em UMA máquina, e `data/raw/` é
ignorado pelo Git de propósito. Manifesto com sha256 não é backup: enquanto os
bytes não estiverem no bucket e tiverem sido **baixados de volta e reconferidos**,
a coleta inteira é reversível por um formatador de disco.

    python3 scripts/adama_it_preservar.py --plano       # offline, sempre roda
    python3 scripts/adama_it_preservar.py --enviar      # exige as duas variáveis
    python3 scripts/adama_it_preservar.py --verificar   # baixa de volta e reconfere

AUTENTICAÇÃO
--------------
Só variável de ambiente já configurada: `SUPABASE_URL` e `SUPABASE_SECRET_KEY`,
os mesmos nomes dos workflows deste repositório. Este arquivo NÃO procura segredo
em disco, não lê `.env`, não imprime chave e não cria credencial. Sem as duas,
`--enviar` recusa e diz exatamente o que falta.

A CHAVE — reusada da cicatriz espanhola, não reinventada
---------------------------------------------------------
    IT/adama-website/<espécie>/<sha16>-<nome-saneado>

É **endereçada por conteúdo**: o sha16 entra no nome. Duas capturas do mesmo
arquivo caem no mesmo lugar; um arquivo que mudou cai em outro. Sobrescrita
silenciosa de conteúdo diferente deixa de ser possível pelo formato da chave.

O saneamento faz NFC antes de tudo — "à" composto e decomposto são o MESMO nome,
e sem normalizar viram duas chaves para um arquivo. Não faz URL-decode: `%20` no
nome não vira espaço aqui, porque decodificar muda a identidade do que foi
baixado. O nome original fica em `ORIGINAL_FILENAME`, no metadata.

    PATH ≠ IDENTITY

OS ESTADOS
-----------
    PENDING                    ainda não tentado
    UPLOADED                   subiu nesta execução
    ALREADY_PRESENT            já estava lá
    ALREADY_PRESENT_VERIFIED   já estava lá E os bytes de volta batem
    VERIFIED                   subiu E os bytes de volta batem
    FAILED_WITH_REASON         não subiu, ou subiu e não bateu — com o motivo

`preservado = true` só depois de VERIFIED ou ALREADY_PRESENT_VERIFIED. Nunca
depois de UPLOADED sozinho: HTTP 200 no upload diz que o servidor aceitou, não
que os bytes certos chegaram.

    RAW PRESENCE ≠ RAW CONTENT VERIFIED

E O 5XX
--------
    HTTP_5XX ≠ OBJECT_NOT_PRESERVED

Medido na Espanha em 30/08/2026: um objeto recebeu 520 no upload e foi carimbado
FAILED — e o inventário remoto provou depois que ele ESTAVA lá. 520 é a resposta
que se perdeu, não a gravação. Antes de chamar de falha, pergunta-se ao bucket.
"""
import datetime
import hashlib
import json
import os
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ACERVO = os.path.join(RAIZ, 'data', 'raw', 'IT', 'adama-website')
AMOSTRAS = os.path.join(RAIZ, 'data', 'samples', 'IT-CATALOGO')
PLANO = os.path.join(AMOSTRAS, 'IT-ADAMA-PRESERVACAO-PLANO.json')
RELATORIO = os.path.join(AMOSTRAS, 'IT-ADAMA-PRESERVACAO-RELATORIO.json')
BUCKET = 'raw'
PREFIXO = 'IT/adama-website'
LIMITE_BYTES = 200 * 1024 * 1024

# Só o que reproduz a evidência. Cache do navegador, CSS, fonte e cookie ficam
# de fora — inflar o denominador faria o portão fechar sobre lixo.
ESPECIES = (
    ('pages', 'PRODUCT_DOM', 'text/html; charset=utf-8'),
    ('documents', 'DOCUMENT', None),
    ('captures', 'CAPTURE', None),
)
MANIFESTOS = ('indice-captura.json', 'enumeracao.json')

_PERMITIDO = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
                 "!-.*'() &$@=;:+,?")
_MAX_SEGMENTO = 120

_MIME = {'.pdf': 'application/pdf', '.html': 'text/html; charset=utf-8',
         '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8',
         '.json': 'application/json', '.docx':
         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
         '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
         '.zip': 'application/zip', '.jpg': 'image/jpeg', '.png': 'image/png'}


def _encurtar(seg):
    """Corta pelo meio do NOME, nunca da extensão — e só quando passa do limite."""
    if len(seg) <= _MAX_SEGMENTO:
        return seg
    raiz, ponto, ext = seg.rpartition('.')
    if ponto and 0 < len(ext) <= 8:
        return raiz[:_MAX_SEGMENTO - len(ext) - 1] + '.' + ext
    return seg[:_MAX_SEGMENTO]


def sanear(bruta):
    """Caminho de objeto seguro e DETERMINÍSTICO. Mesmo asset, sempre a mesma chave."""
    fora = []
    for seg in unicodedata.normalize('NFC', bruta or '').split('/'):
        if not seg:
            continue
        base = ''.join(c for c in unicodedata.normalize('NFD', seg)
                       if unicodedata.category(c) != 'Mn')
        limpo = _encurtar(''.join(c if c in _PERMITIDO else '_' for c in base))
        fora.append(limpo if limpo.strip('.') else '_')
    return '/'.join(fora)


def chave_de_storage(especie, sha256, nome):
    """Endereçada por conteúdo: o sha16 no nome impede sobrescrita silenciosa."""
    return sanear('%s/%s/%s-%s' % (PREFIXO, especie, sha256[:16], nome))


def _sha_e_bytes(caminho):
    h, n = hashlib.sha256(), 0
    with open(caminho, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
            n += len(b)
    return h.hexdigest(), n


def _mime(caminho, padrao=None):
    return _MIME.get(os.path.splitext(caminho)[1].lower(),
                     padrao or 'application/octet-stream')


def _nomes_originais():
    """media_id → nome como o servidor entregou. Vai para o metadata, não para a chave."""
    fora = {}
    for nome in ('documentos-censo.json', 'documentos-amostra.json'):
        caminho = os.path.join(ACERVO, nome)
        if not os.path.exists(caminho):
            continue
        with open(caminho, encoding='utf-8') as fh:
            for d in json.load(fh).get('DOCUMENTS', []):
                if d.get('STATE') == 'DOWNLOADED' and d.get('LOCAL_FILE'):
                    fora[os.path.basename(d['LOCAL_FILE'])] = {
                        'ORIGINAL_FILENAME': d.get('ORIGINAL_FILENAME'),
                        'SOURCE_URL': d.get('SOURCE_URL'),
                        'PRODUCT_URL': d.get('PRODUCT_URL')}
    return fora


def plano():
    """Assets a preservar, com hash RECALCULADO do disco agora.

    Não confia no manifesto: o manifesto diz o que foi baixado, o disco diz o que
    existe. Divergência entre os dois é achado, não detalhe.
    """
    meta_docs = _nomes_originais()
    itens = []
    for pasta, especie, mime_padrao in ESPECIES:
        base = os.path.join(ACERVO, pasta)
        if not os.path.isdir(base):
            continue
        for nome in sorted(os.listdir(base)):
            caminho = os.path.join(base, nome)
            if not os.path.isfile(caminho):
                continue
            sha, n = _sha_e_bytes(caminho)
            extra = meta_docs.get(nome, {})
            itens.append({
                'ESPECIE': especie,
                'ARQUIVO_LOCAL': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
                'OBJETO': chave_de_storage(especie, sha, nome),
                'SHA256': sha, 'BYTES': n,
                'MEDIA_TYPE': _mime(caminho, mime_padrao),
                'ORIGINAL_FILENAME': extra.get('ORIGINAL_FILENAME') or nome,
                'SOURCE_URL': extra.get('SOURCE_URL'),
                'PRODUCT_URL': extra.get('PRODUCT_URL'),
                'COUNTRY': 'IT', 'ESTADO': 'PENDING'})
    for nome in MANIFESTOS:
        caminho = os.path.join(ACERVO, nome)
        if not os.path.exists(caminho):
            continue
        sha, n = _sha_e_bytes(caminho)
        itens.append({
            'ESPECIE': 'MANIFEST',
            'ARQUIVO_LOCAL': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
            'OBJETO': chave_de_storage('MANIFEST', sha, nome),
            'SHA256': sha, 'BYTES': n, 'MEDIA_TYPE': 'application/json',
            'ORIGINAL_FILENAME': nome, 'SOURCE_URL': None, 'PRODUCT_URL': None,
            'COUNTRY': 'IT', 'ESTADO': 'PENDING'})

    chaves = {}
    for it in itens:
        chaves.setdefault(it['OBJETO'], []).append(it['ARQUIVO_LOCAL'])
    colisoes = {k: v for k, v in chaves.items() if len(v) > 1}
    maior = max((i['BYTES'] for i in itens), default=0)
    hoje = datetime.date.today().isoformat()
    return {
        'SOURCE_ID': 'IT-ADAMA-CATALOG',
        'source': ('acervo local data/raw/IT/adama-website/, capturado do catálogo '
                   'público ADAMA Italia pelo Chrome com janela desta máquina'),
        'captured_at': hoje, 'CAPTURED_AT': hoje,
        'SOURCE_COUNTRY': 'IT', 'FACT_COUNTRY': 'IT',
        'EVIDENCE_CLASS': 'PRESERVATION_PLAN',
        'WHAT_THIS_IS_NOT': ('prova de preservação. É a lista do que precisa subir, '
                             'com o hash lido do disco agora. A prova só existe '
                             'depois do download de volta com sha conferido'),
        'PAIS': 'IT', 'BUCKET': BUCKET, 'PREFIXO': PREFIXO,
        'RAW_EXPECTED': len(itens),
        'OBJETOS_DISTINTOS': len(chaves),
        'COLISOES_DE_CHAVE': colisoes,
        'POR_ESPECIE': _contar(itens, 'ESPECIE'),
        'BYTES_TOTAIS': sum(i['BYTES'] for i in itens),
        'LARGEST_ASSET_BYTES': maior,
        'LIMITE_BYTES': LIMITE_BYTES,
        'MAIOR_CABE_NO_LIMITE': maior < LIMITE_BYTES,
        'O_QUE_NAO_ENTRA': ['cache do navegador', 'CSS', 'fontes', 'cookies',
                            'perfil do Chrome', 'estado do DevTools'],
        'ITENS': itens,
    }


def _contar(itens, campo):
    fora = {}
    for i in itens:
        fora[i.get(campo)] = fora.get(i.get(campo), 0) + 1
    return fora


# ─────────────────────────────────────────────────────────── rede
def autenticacao():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    key = os.environ.get('SUPABASE_SECRET_KEY', '')
    faltam = [n for n, v in (('SUPABASE_URL', url), ('SUPABASE_SECRET_KEY', key)) if not v]
    return url, key, faltam


def _http(url, key, metodo, caminho, dados=None, ctype=None, timeout=300):
    cab = {'apikey': key, 'Authorization': 'Bearer ' + key}
    if ctype:
        cab['Content-Type'] = ctype
    req = urllib.request.Request(url + caminho, data=dados, method=metodo, headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:                                   # rede caiu, DNS, TLS
        return 0, ('%s: %s' % (type(e).__name__, e)).encode()[:300]


def inventario_remoto(url, key, prefixo=PREFIXO):
    """O que o bucket diz que tem. A verdade do estado é o objeto remoto."""
    vistos, pilha = {}, [prefixo]
    while pilha:
        atual = pilha.pop()
        corpo = json.dumps({'prefix': atual, 'limit': 1000,
                            'sortBy': {'column': 'name', 'order': 'asc'}}).encode()
        st, body = _http(url, key, 'POST', '/storage/v1/object/list/' + BUCKET,
                         corpo, 'application/json')
        if st != 200:
            return None, 'list %s devolveu HTTP %s: %s' % (atual, st, body[:120])
        for o in json.loads(body):
            nome = '%s/%s' % (atual, o['name'])
            if o.get('id') is None:
                pilha.append(nome)
            else:
                vistos[nome] = (o.get('metadata') or {}).get('size')
    return vistos, None


def enviar(itens, url, key, verificar=True):
    for it in itens:
        caminho = os.path.join(RAIZ, it['ARQUIVO_LOCAL'].replace('/', os.sep))
        try:
            with open(caminho, 'rb') as f:
                corpo = f.read()
        except OSError as e:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'não consegui ler o arquivo local: %s' % type(e).__name__
            continue
        if hashlib.sha256(corpo).hexdigest() != it['SHA256'] or len(corpo) != it['BYTES']:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'o arquivo mudou entre o plano e o envio'
            continue

        alvo = '/storage/v1/object/%s/%s' % (BUCKET, urllib.parse.quote(it['OBJETO']))
        st, body = _http(url, key, 'POST', alvo, corpo, it['MEDIA_TYPE'])
        if st in (200, 201):
            it['ESTADO'] = 'UPLOADED'
        elif st == 409 or b'already exists' in body or b'Duplicate' in body:
            it['ESTADO'] = 'ALREADY_PRESENT'
        else:
            # HTTP_5XX ≠ OBJECT_NOT_PRESERVED — pergunta-se ao bucket antes de
            # carimbar falha.
            st2, volta = _http(url, key, 'GET', alvo)
            if (st2 == 200 and len(volta) == it['BYTES']
                    and hashlib.sha256(volta).hexdigest() == it['SHA256']):
                it['ESTADO'] = 'ALREADY_PRESENT_VERIFIED'
                it['VERIFICACAO'] = 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'
                it['RESPOSTA_AMBIGUA'] = {
                    'HTTP_NO_UPLOAD': st,
                    'PORQUE_NAO_E_FALHA': ('o upload devolveu %s, mas o objeto está no '
                                           'bucket e os bytes de volta batem com o '
                                           'sha256 local' % st)}
                continue
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'upload devolveu HTTP %s: %s' % (st, body[:160].decode(
                'utf-8', 'replace'))
            it['CONFERENCIA_REMOTA_APOS_FALHA'] = {'HTTP_NO_GET': st2,
                                                   'BYTES_DE_VOLTA': len(volta or b'')}
            continue
        if verificar:
            verificar_um(it, url, key)
    return itens


def verificar_um(it, url, key):
    """Baixa de volta e reconfere. É aqui que a preservação fecha."""
    alvo = '/storage/v1/object/%s/%s' % (BUCKET, urllib.parse.quote(it['OBJETO']))
    st, volta = _http(url, key, 'GET', alvo)
    if st != 200:
        it['ESTADO'] = 'FAILED_WITH_REASON'
        it['MOTIVO'] = 'download de volta devolveu HTTP %s' % st
        it['PRESERVADO'] = False
        return it
    sha = hashlib.sha256(volta).hexdigest()
    it['SHA256_REMOTO'] = sha
    it['BYTES_DE_VOLTA'] = len(volta)
    if sha == it['SHA256'] and len(volta) == it['BYTES']:
        it['ESTADO'] = ('ALREADY_PRESENT_VERIFIED'
                        if it['ESTADO'] == 'ALREADY_PRESENT' else 'VERIFIED')
        it['VERIFICACAO'] = 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'
        it['PRESERVADO'] = True
    else:
        it['ESTADO'] = 'FAILED_WITH_REASON'
        it['MOTIVO'] = 'HASH_MISMATCH: os bytes de volta não batem com os locais'
        it['PRESERVADO'] = False
    return it


VERIFICADOS = ('VERIFIED', 'ALREADY_PRESENT_VERIFIED')


def portao(itens, esperado, remoto=None):
    """As sete condições. A sétima é a que conta."""
    presentes = sum(1 for i in itens if i['ESTADO'] in VERIFICADOS
                    or i['ESTADO'] in ('UPLOADED', 'ALREADY_PRESENT'))
    conferidos = sum(1 for i in itens if i.get('VERIFICACAO'))
    verificados = sum(1 for i in itens if i['ESTADO'] in VERIFICADOS)
    divergentes = sum(1 for i in itens
                      if str(i.get('MOTIVO', '')).startswith('HASH_MISMATCH'))
    falhos = sum(1 for i in itens if i['ESTADO'] == 'FAILED_WITH_REASON') - divergentes
    esperadas = {i['OBJETO'] for i in itens}
    orfaos = len([k for k in (remoto or {}) if k not in esperadas])
    return dict(rw.gate(esperado=esperado, remoto_presente=presentes,
                        remoto_ausente=esperado - presentes, orfaos=orfaos,
                        falhos=max(falhos, 0), hash_conferido=conferidos,
                        hash_divergente=divergentes),
                SHA_VERIFIED=verificados,
                REMOTE_INVENTORY_READ=remoto is not None)


sys.path.insert(0, AQUI)
import adama_it_raw as rw   # noqa: E402


def main():
    p = plano()
    os.makedirs(AMOSTRAS, exist_ok=True)
    with open(PLANO, 'w', encoding='utf-8') as fh:
        json.dump(p, fh, ensure_ascii=False, indent=2)
    print('RAW_EXPECTED         :', p['RAW_EXPECTED'])
    print('objetos distintos    :', p['OBJETOS_DISTINTOS'])
    print('colisões de chave    :', len(p['COLISOES_DE_CHAVE']))
    print('por espécie          :', p['POR_ESPECIE'])
    print('bytes totais         : %d (%.1f MB)' % (p['BYTES_TOTAIS'],
                                                   p['BYTES_TOTAIS'] / 1048576))
    print('LARGEST_ASSET_BYTES  : %d (cabe no limite de 200 MB: %s)'
          % (p['LARGEST_ASSET_BYTES'], p['MAIOR_CABE_NO_LIMITE']))
    print('->', os.path.relpath(PLANO, RAIZ))

    if '--enviar' not in sys.argv and '--verificar' not in sys.argv:
        return 0

    url, key, faltam = autenticacao()
    if faltam:
        print()
        print('SEM CREDENCIAL — não envio nada.')
        print('  faltam as variáveis de ambiente:', ', '.join(faltam))
        print('  este arquivo não lê .env, não procura segredo em disco e não')
        print('  cria credencial. RAW_PRESERVATION_GATE_IT continua OPEN.')
        return 3

    if not p['MAIOR_CABE_NO_LIMITE']:
        print('PARADO: o maior asset passa do limite de 200 MB.')
        return 4

    remoto, erro = inventario_remoto(url, key)
    if erro:
        print('inventário remoto falhou:', erro)
        remoto = None
    itens = p['ITENS']
    if '--enviar' in sys.argv:
        enviar(itens, url, key)
    else:
        for it in itens:
            verificar_um(it, url, key)
    if remoto is None:
        remoto, _ = inventario_remoto(url, key)

    g = portao(itens, p['RAW_EXPECTED'], remoto)
    rel = {'SOURCE_ID': 'IT-ADAMA-CATALOG', 'source': p['source'],
           'captured_at': p['captured_at'], 'CAPTURED_AT': p['CAPTURED_AT'],
           'SOURCE_COUNTRY': 'IT', 'EVIDENCE_CLASS': 'PRESERVATION_PROOF',
           'PAIS': 'IT', 'RAW_EXPECTED': p['RAW_EXPECTED'],
           'POR_ESTADO': _contar(itens, 'ESTADO'), 'GATE': g, 'ITENS': itens}
    with open(RELATORIO, 'w', encoding='utf-8') as fh:
        json.dump(rel, fh, ensure_ascii=False, indent=2)
    print()
    print('por estado           :', rel['POR_ESTADO'])
    print('SHA_VERIFIED         :', g['SHA_VERIFIED'])
    print('HASH_MISMATCH        :', g['HASH_MISMATCH'])
    print('ORPHANS              :', g['ORPHANS'])
    print('FAILED               :', g['FAILED'])
    print('RAW_PRESERVATION_GATE_IT =', 'CLOSED' if g['STATE'] == 'CLOSED' else 'OPEN')
    if g['MISSING']:
        print('  faltam             :', ', '.join(g['MISSING']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
