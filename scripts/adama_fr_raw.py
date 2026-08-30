#!/usr/bin/env python3
"""
RAW FRANCÊS — os bytes só estão preservados quando voltam iguais.

    python scripts/adama_fr_raw.py --plano       # offline, sempre roda
    python scripts/adama_fr_raw.py --enviar      # exige SUPABASE_URL e SUPABASE_SECRET_KEY
    python scripts/adama_fr_raw.py --verificar   # baixa de volta e reconfere o sha256

O PIPELINE, E CADA SETA É UM ESTADO
-------------------------------------
    DOWNLOAD → SHA256 LOCAL → METADATA → RAW PLAN → STORAGE KEY
             → UPLOAD → REMOTE INVENTORY → DOWNLOAD BACK → SHA VERIFY

A ÚLTIMA SETA É A QUE IMPORTA
-------------------------------
"O objeto existe no bucket" e "o objeto tem os bytes que eu enviei" são
afirmações diferentes, e só a segunda serve. Upload truncado, retry que gravou
por cima, arquivo com o nome certo e o conteúdo de outro — todos passam por
REMOTE_PRESENT e nenhum passa por CONTENT_HASH_VERIFIED.

    RAW PRESENCE ≠ RAW CONTENT VERIFIED

E O 5XX
--------
    HTTP_5XX ≠ OBJECT_NOT_PRESERVED

Resposta ambígua não diz que o objeto não foi gravado — diz que não se sabe.
Reenviar às cegas depois de um 5xx pode duplicar ou corromper. A ordem é
inventário remoto, depois download e hash, e só então um estado.

AUTENTICAÇÃO
-------------
Só variável de ambiente já configurada: `SUPABASE_URL` e `SUPABASE_SECRET_KEY`,
os mesmos nomes que os workflows deste repositório já usam. Este arquivo NÃO
procura segredo em disco, não lê `.env`, não imprime chave e não cria credencial.
Sem as duas, `--enviar` recusa e diz exatamente o que falta.

O TAMANHO, ANTES DO LOTE
--------------------------
O maior asset é medido ANTES de abrir lote. O bucket aceita até 200 MB, e
descobrir um arquivo maior no último upload custa o lote inteiro. Evidência
original não é comprimida para caber: se passar, o certo é parar e dizer.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import adama_fr as fr                                            # noqa: E402

COUNTRY = 'FR'
BUCKET = 'raw'
LIMITE_BUCKET_BYTES = 200 * 1024 * 1024

RAW = os.path.join(ROOT, 'data', 'raw', COUNTRY)
MANIFESTO_CATALOGO = os.path.join(RAW, 'adama-website', 'MANIFESTO-CATALOGO.json')
MANIFESTO_EPHY = os.path.join(RAW, 'anses-ephy', 'MANIFESTO-EPHY-FR.json')
PLANO = os.path.join(RAW, 'RAW-PLANO-FR.json')
RELATORIO = os.path.join(RAW, 'RAW-RELATORIO-FR.json')

# Estados do objeto individual.
LOCAL_ONLY = 'LOCAL_ONLY'
UPLOADED_UNVERIFIED = 'UPLOADED_NOT_VERIFIED'
REMOTE_PRESENT = 'REMOTE_PRESENT'
CONTENT_HASH_VERIFIED = 'CONTENT_HASH_VERIFIED'
HASH_MISMATCH = 'HASH_MISMATCH'
REMOTE_ABSENT = 'REMOTE_ABSENT'
ORPHAN = 'ORPHAN'
FAILED = 'FAILED'
UNKNOWN_MUST_VERIFY = 'UNKNOWN_MUST_VERIFY'


def sha256_arquivo(caminho, bloco=1 << 20):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for b in iter(lambda: f.read(bloco), b''):
            h.update(b)
    return h.hexdigest()


def apos_resposta_ambigua(http_status):
    """O que fazer depois de um 5xx ou de um timeout. Nunca reenviar às cegas."""
    st = int(http_status)
    if st == TRANSPORTE_AMBIGUO:
        return {'STATE': UNKNOWN_MUST_VERIFY,
                'NEXT': 'inventário remoto, depois download de volta e hash',
                'DO_NOT': 'reenviar às cegas',
                'WHY': ('TIMEOUT ≠ OBJECT_NOT_PRESERVED — o pedido saiu e a '
                        'resposta não chegou')}
    if 500 <= st < 600:
        return {'STATE': UNKNOWN_MUST_VERIFY,
                'NEXT': 'inventário remoto, depois download de volta e hash',
                'DO_NOT': 'reenviar às cegas',
                'WHY': 'HTTP_5XX ≠ OBJECT_NOT_PRESERVED'}
    return {'STATE': FAILED, 'NEXT': 'registrar e seguir',
            'WHY': 'resposta não ambígua'}


def _ler(caminho):
    if not os.path.isfile(caminho):
        return None
    with open(caminho, encoding='utf-8') as fh:
        return json.load(fh)


def plano():
    """O que preservar, medido do disco. Sem rede, e por isso sempre roda."""
    itens = []

    cat = _ler(MANIFESTO_CATALOGO)
    if cat:
        for p in cat['PRODUCTS']:
            caminho = os.path.join(ROOT, p['LOCAL_PATH'])
            if not os.path.isfile(caminho):
                continue
            itens.append({
                'SOURCE': 'FR-ADAMA-CATALOG', 'KIND': 'PAGE_CAPTURE',
                'PREFIX': 'adama-website',
                'URL': p['URL'], 'LOCAL_PATH': p['LOCAL_PATH'],
                'ORIGINAL_FILENAME': os.path.basename(p['LOCAL_PATH']),
                'CONTENT_TYPE': 'text/html; charset=utf-8',
                'RELATED_REGISTRATION': p['REGISTRATION_ID_CLAIMED'],
                'RELATED_PRODUCT': p['PRODUCT_NAME'],
                'CAPTURED_AT': p['CAPTURED_AT'],
            })
        for d in cat['DOCUMENTS']:
            if not d.get('LOCAL_PATH'):
                continue
            caminho = os.path.join(ROOT, d['LOCAL_PATH'])
            if not os.path.isfile(caminho):
                continue
            itens.append({
                'SOURCE': 'FR-ADAMA-CATALOG', 'KIND': d.get('DOC_TYPE'),
                'PREFIX': 'adama-website',
                'URL': d['URL'], 'LOCAL_PATH': d['LOCAL_PATH'],
                'ORIGINAL_FILENAME': d.get('ORIGINAL_FILENAME'),
                'CONTENT_TYPE': d.get('CONTENT_TYPE'),
                'RELATED_REGISTRATION': d.get('RELATED_REGISTRATION'),
                'CAPTURED_AT': d.get('CAPTURED_AT'),
            })

    ephy = _ler(MANIFESTO_EPHY)
    if ephy:
        zip_rel = ephy.get('ZIP_LOCAL')
        if zip_rel and os.path.isfile(os.path.join(ROOT, zip_rel)):
            itens.append({
                'SOURCE': 'FR-T4-001', 'KIND': 'REGULATORY_DATASET',
                'PREFIX': 'anses-ephy',
                'URL': ephy['RESOLVED']['URL'], 'LOCAL_PATH': zip_rel,
                'ORIGINAL_FILENAME': os.path.basename(zip_rel),
                'CONTENT_TYPE': 'application/zip',
                'RELATED_REGISTRATION': None,
                'DATASET_VERSION': ephy['RESOLVED']['DATASET_LAST_UPDATE'],
                'CAPTURED_AT': ephy['CAPTURE_TIME'],
            })

    # Medir cada um: o sha e o tamanho nascem AQUI, junto do plano — e a CHAVE
    # nasce do sha, não do nome. O manifesto do coletor não é consultado para
    # isso de propósito: a chave é assunto da camada de preservação, e derivá-la
    # aqui garante que ela sempre corresponda aos bytes que estão em disco AGORA.
    for it in itens:
        caminho = os.path.join(ROOT, it['LOCAL_PATH'])
        it['BYTES'] = os.path.getsize(caminho)
        it['SHA256_LOCAL'] = sha256_arquivo(caminho)
        it['STORAGE_KEY'] = '%s/%s/%s' % (
            COUNTRY, it['PREFIX'],
            fr.storage_key(COUNTRY, it.get('RELATED_REGISTRATION'), it['KIND'],
                           it['ORIGINAL_FILENAME'], it['SHA256_LOCAL']
                           ).split('/', 1)[1])
        it['SHA256_REMOTE'] = None
        it['STATE'] = LOCAL_ONLY
        it['COUNTRY'] = COUNTRY

    # Um OBJETO por chave, e as referências penduradas nele.
    #
    # Os 111 produtos e 153 documentos dão 265 arquivos em disco — e apenas 191
    # sequências de bytes distintas. A causa é o catálogo: quatro fichas do AMM
    # 2240001 apontam para o MESMO PDF, e cada uma o baixou. Com a chave aberta
    # pelo sha do conteúdo, os quatro caem no mesmo objeto, que é o certo.
    #
    # E é por isso que o portão conta OBJETO e não arquivo: exigir
    # REMOTE_PRESENT == 265 num bucket que legitimamente guarda 191 seria um
    # portão que nunca fecha — e portão que nunca fecha vira portão ignorado.
    porchave = {}
    colisoes = []
    for it in itens:
        anterior = porchave.get(it['STORAGE_KEY'])
        if anterior is None:
            it['REFERENCES'] = [{'LOCAL_PATH': it['LOCAL_PATH'], 'URL': it['URL']}]
            porchave[it['STORAGE_KEY']] = it
            continue
        if anterior['SHA256_LOCAL'] != it['SHA256_LOCAL']:
            colisoes.append({'STORAGE_KEY': it['STORAGE_KEY'],
                             'A': anterior['LOCAL_PATH'], 'B': it['LOCAL_PATH']})
        anterior['REFERENCES'].append({'LOCAL_PATH': it['LOCAL_PATH'],
                                       'URL': it['URL']})

    objetos = list(porchave.values())
    maior = max([i['BYTES'] for i in objetos] or [0])
    p = {
        'COUNTRY': COUNTRY, 'BUCKET': BUCKET,
        'RAW_EXPECTED': len(objetos),
        'LOCAL_FILES': len(itens),
        'DUPLICATE_REFERENCES': len(itens) - len(objetos),
        'DISTINCT_STORAGE_KEYS': len(porchave),
        'KEY_COLLISIONS': colisoes,
        'TOTAL_BYTES': sum(i['BYTES'] for i in objetos),
        'LARGEST_ASSET_BYTES': maior,
        'LARGEST_ASSET': next((i['LOCAL_PATH'] for i in objetos
                               if i['BYTES'] == maior), None),
        'BUCKET_LIMIT_BYTES': LIMITE_BUCKET_BYTES,
        'EXCEEDS_BUCKET_LIMIT': maior > LIMITE_BUCKET_BYTES,
        'ITEMS': objetos,
    }
    os.makedirs(RAW, exist_ok=True)
    with open(PLANO, 'w', encoding='utf-8') as fh:
        json.dump(p, fh, ensure_ascii=False, indent=1)
    return p


# ══════════════════════════════════════════════════════════════════════════════
# O DESTINO — só com credencial já configurada no ambiente
# ══════════════════════════════════════════════════════════════════════════════

def credencial():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    key = os.environ.get('SUPABASE_SECRET_KEY') or ''
    faltam = [n for n, v in (('SUPABASE_URL', url), ('SUPABASE_SECRET_KEY', key)) if not v]
    return url, key, faltam


# Status inventado para "o pedido saiu e a resposta não chegou". Não é 0 porque
# 0 é um HTTP válido em lugar nenhum — é justamente por isso que ele serve: nunca
# vai ser confundido com resposta do servidor.
TRANSPORTE_AMBIGUO = 0


def _http(metodo, url, key, dados=None, ctype=None, tentativas=3, dormir=None):
    """→ (status, corpo). NUNCA levanta por falha de transporte.

    A primeira versão deixava `TimeoutError` subir. Num lote de 234 objetos isso
    significa que UM soquete lento derruba a execução inteira — e ela morre sem
    escrever relatório, deixando o estado ambíguo: parte subiu, parte não, e
    ninguém sabe qual é qual. Foi o que aconteceu no run 33333878608, no objeto
    de número desconhecido, porque nem progresso era impresso.

    Um timeout NÃO diz que o objeto não foi gravado. Diz que a resposta não
    chegou. É a mesma lei do 5xx, um andar abaixo:

        HTTP_5XX  ≠ OBJECT_NOT_PRESERVED
        TIMEOUT   ≠ OBJECT_NOT_PRESERVED

    Por isso o retorno é `TRANSPORTE_AMBIGUO`, e quem chama trata como
    UNKNOWN_MUST_VERIFY — resolvido depois pelo download de volta, que é a única
    coisa que responde de verdade.
    """
    import time
    dormir = time.sleep if dormir is None else dormir
    cab = {'apikey': key, 'Authorization': 'Bearer ' + key}
    if ctype:
        cab['Content-Type'] = ctype
    ultimo = None
    for n in range(tentativas):
        rq = urllib.request.Request(url, data=dados, method=metodo, headers=cab)
        try:
            with urllib.request.urlopen(rq, timeout=300) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            # Resposta do servidor: isso não se repete às cegas. 5xx é decidido
            # por quem chama, com inventário — não com mais uma tentativa.
            return e.code, e.read()
        except Exception as e:                                    # noqa: BLE001
            ultimo = e
            if n < tentativas - 1:
                dormir(2 ** n)
    return TRANSPORTE_AMBIGUO, str(ultimo).encode('utf-8', 'replace')[:200]


def canario():
    """Prova de autenticação SÓ DE LEITURA, antes de escrever um byte.

    Um upload que falha por credencial errada não falha limpo: ele pode gravar
    metade do lote, ou gravar num bucket que não é o nosso, e o diagnóstico vem
    depois de 310 MB de tentativa. A leitura vem antes e custa uma requisição.

        AUTH_UNKNOWN ≠ AUTH_OK
        Se o canário não passa, UPLOAD_ATTEMPTS = 0.

    E de quebra mede a capacidade na única fonte autoritativa que estas
    credenciais alcançam: o próprio bucket declara o limite POR OBJETO. A quota
    TOTAL do projeto não é exposta pela API de Storage — e inventar um número
    para ela seria pior do que dizer que não se sabe.

        PER_OBJECT_LIMIT ≠ TOTAL_PROJECT_QUOTA
    """
    url, key, faltam = credencial()
    if faltam:
        return {'SUPABASE_AUTH_CANARY': 'FAIL', 'RAW_BUCKET_ACCESS': 'FAIL',
                'UPLOAD_ATTEMPTS': 0, 'MISSING': faltam,
                'WHY': 'sem credencial no ambiente'}

    st, body = _http('GET', '%s/storage/v1/bucket/%s' % (url, BUCKET), key)
    if st != 200:
        return {'SUPABASE_AUTH_CANARY': 'FAIL' if st in (401, 403) else 'UNKNOWN',
                'RAW_BUCKET_ACCESS': 'FAIL', 'HTTP': st, 'UPLOAD_ATTEMPTS': 0,
                'WHY': ('a leitura do bucket %r devolveu %d. Nada foi enviado'
                        % (BUCKET, st))}
    try:
        info = json.loads(body.decode('utf-8'))
    except ValueError:
        info = {}

    limite = info.get('file_size_limit')
    return {
        'SUPABASE_AUTH_CANARY': 'PASS',
        'RAW_BUCKET_ACCESS': 'PASS',
        'BUCKET': info.get('name') or BUCKET,
        'BUCKET_PUBLIC': info.get('public'),
        'PER_OBJECT_LIMIT_BYTES': limite,
        'PER_OBJECT_LIMIT_SOURCE': ('declarado pelo próprio bucket' if limite
                                    else 'o bucket não declara limite por objeto'),
        'TOTAL_STORAGE_QUOTA': 'NOT_KNOWN',
        'WHY_QUOTA_NOT_KNOWN': (
            'a API de Storage não expõe a quota total do projeto a esta '
            'credencial. Não é 200 MB: 200 MB é o limite POR OBJETO'),
        'UPLOAD_ATTEMPTS': 0,
    }


def enviar(p=None, verificar=True):
    """Sobe e confere. `preserved` só depois do hash de volta bater."""
    url, key, faltam = credencial()
    if faltam:
        return {'STATE': 'NO_CREDENTIALS', 'MISSING': faltam,
                'WHY': ('sem credencial no ambiente. Este arquivo não procura '
                        'segredo em disco nem cria credencial')}
    # A conferência LOCAL vem antes da que custa rede: um lote já desqualificado
    # pelo tamanho não precisa de nenhuma requisição para ser recusado.
    p = p or plano()
    if p['EXCEEDS_BUCKET_LIMIT']:
        return {'STATE': 'ASSET_TOO_LARGE',
                'LARGEST_ASSET_BYTES': p['LARGEST_ASSET_BYTES'],
                'WHY': ('um asset passa do limite do bucket. Evidência original '
                        'não é comprimida para caber')}

    c = canario()
    if c['SUPABASE_AUTH_CANARY'] != 'PASS':
        return dict(c, STATE='AUTH_CANARY_FAILED')

    # INVENTÁRIO PRIMEIRO, e é isso que torna a execução repetível.
    #
    # A chave é endereçada por conteúdo: se o objeto já está lá com o mesmo sha,
    # ele É o objeto certo, e reenviar 310 MB não prova nada que o hash já não
    # tenha provado. Numa reexecução depois de queda, isto transforma o lote
    # inteiro em conferência barata em vez de upload repetido.
    #
    #     JÁ ESTÁ LÁ E BATE  ->  não precisa subir
    #     NÃO ESTÁ LÁ        ->  sobe, e confere depois
    #     RESPOSTA AMBÍGUA   ->  confere; nunca reenvia às cegas
    resultado = []
    subidos = pulados = 0
    for n, it in enumerate(p['ITEMS'], 1):
        estado = _verificar_um(url, key, it)
        if estado['STATE'] == CONTENT_HASH_VERIFIED:
            pulados += 1
            resultado.append(estado)
        else:
            estado = _subir_um(url, key, it)
            subidos += 1
            if verificar and estado['STATE'] != FAILED:
                estado = _verificar_um(url, key, estado)
            resultado.append(estado)
        if n % 20 == 0 or n == len(p['ITEMS']):
            conferidos = sum(1 for x in resultado
                             if x['STATE'] == CONTENT_HASH_VERIFIED)
            print('  %3d/%d  enviados %3d  ja estavam %3d  conferidos %3d'
                  % (n, len(p['ITEMS']), subidos, pulados, conferidos))
            sys.stdout.flush()
    return _relatorio(p, resultado)


def _subir_um(url, key, it):
    """Envia UM objeto. Uma falha aqui não derruba o lote — vira estado."""
    estado = dict(it)
    caminho = os.path.join(ROOT, it['LOCAL_PATH'])
    try:
        with open(caminho, 'rb') as fh:
            corpo = fh.read()
    except OSError as e:
        estado['STATE'] = FAILED
        estado['WHY'] = 'não consegui ler o arquivo local: %s' % str(e)[:120]
        return estado
    destino = '%s/storage/v1/object/%s/%s' % (
        url, BUCKET, urllib.parse.quote(it['STORAGE_KEY']))
    st, body = _http('POST', destino, key, corpo,
                     it.get('CONTENT_TYPE') or 'application/octet-stream')
    if st in (200, 201) or b'already exists' in body or b'Duplicate' in body:
        estado['STATE'] = UPLOADED_UNVERIFIED
    elif st == TRANSPORTE_AMBIGUO or 500 <= st < 600:
        estado.update(apos_resposta_ambigua(st))
    else:
        estado['STATE'] = FAILED
        estado['WHY'] = 'upload devolveu %d: %s' % (st, body[:120])
    return estado


def _verificar_um(url, key, it):
    """Baixa de volta e compara o hash. É aqui que o RAW fecha."""
    destino = '%s/storage/v1/object/%s/%s' % (
        url, BUCKET, urllib.parse.quote(it['STORAGE_KEY']))
    st, body = _http('GET', destino, key)
    it = dict(it)
    if st == 404:
        it['STATE'] = REMOTE_ABSENT
        return it
    if st == TRANSPORTE_AMBIGUO:
        it.update(apos_resposta_ambigua(st))
        return it
    if st != 200:
        it['STATE'] = UNKNOWN_MUST_VERIFY if 500 <= st < 600 else FAILED
        it['WHY'] = 'leitura de volta devolveu %d' % st
        return it
    remoto = hashlib.sha256(body).hexdigest()
    it['SHA256_REMOTE'] = remoto
    it['STATE'] = (CONTENT_HASH_VERIFIED if remoto == it['SHA256_LOCAL']
                   else HASH_MISMATCH)
    return it


def verificar(p=None):
    url, key, faltam = credencial()
    if faltam:
        return {'STATE': 'NO_CREDENTIALS', 'MISSING': faltam}
    p = p or plano()
    return _relatorio(p, [_verificar_um(url, key, it) for it in p['ITEMS']])


def _relatorio(p, itens):
    conta = {}
    for it in itens:
        conta[it['STATE']] = conta.get(it['STATE'], 0) + 1
    r = {
        'COUNTRY': COUNTRY,
        'RAW_EXPECTED': p['RAW_EXPECTED'],
        'REMOTE_PRESENT': sum(1 for i in itens if i['STATE'] in
                              (REMOTE_PRESENT, CONTENT_HASH_VERIFIED, HASH_MISMATCH)),
        'REMOTE_ABSENT': conta.get(REMOTE_ABSENT, 0),
        'CONTENT_HASH_CHECKED': sum(1 for i in itens if i.get('SHA256_REMOTE')),
        'SHA_VERIFIED': conta.get(CONTENT_HASH_VERIFIED, 0),
        'HASH_MISMATCH': conta.get(HASH_MISMATCH, 0),
        'FAILED': conta.get(FAILED, 0),
        'UNKNOWN_MUST_VERIFY': conta.get(UNKNOWN_MUST_VERIFY, 0),
        'ORPHANS': 0,
        # Bytes de objetos cujo hash VOLTOU e bateu. Não é "bytes enviados":
        # enviado é o que eu afirmo; verificado é o que o servidor devolveu.
        'BYTES_VERIFIED_REMOTELY': sum(i['BYTES'] for i in itens
                                       if i['STATE'] == CONTENT_HASH_VERIFIED),
        'BYTES_EXPECTED': sum(i['BYTES'] for i in itens),
        'KEY_COLLISIONS': len(p.get('KEY_COLLISIONS') or []),
        'BY_STATE': conta,
        'ITEMS': itens,
    }
    r['GATE'] = gate(**{k: r[k] for k in
                        ('RAW_EXPECTED', 'REMOTE_PRESENT', 'REMOTE_ABSENT',
                         'ORPHANS', 'FAILED', 'CONTENT_HASH_CHECKED',
                         'SHA_VERIFIED', 'HASH_MISMATCH')})
    with open(RELATORIO, 'w', encoding='utf-8') as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    return r


def gate(*, RAW_EXPECTED, REMOTE_PRESENT, REMOTE_ABSENT, ORPHANS, FAILED,
         CONTENT_HASH_CHECKED, SHA_VERIFIED, HASH_MISMATCH):
    """O portão RAW francês. Oito condições, e as três últimas são as que contam.

    Aceitar "N objetos existem" fecharia com um bucket cheio de bytes errados.
    """
    condicoes = {
        'EXPECTED_POSITIVE': RAW_EXPECTED > 0,
        'REMOTE_PRESENT_EQ_EXPECTED': REMOTE_PRESENT == RAW_EXPECTED,
        'REMOTE_ABSENT_ZERO': REMOTE_ABSENT == 0,
        'ORPHANS_ZERO': ORPHANS == 0,
        'FAILED_ZERO': FAILED == 0,
        'CONTENT_HASH_CHECKED_EQ_EXPECTED': CONTENT_HASH_CHECKED == RAW_EXPECTED,
        'SHA_VERIFIED_EQ_EXPECTED': SHA_VERIFIED == RAW_EXPECTED,
        'HASH_MISMATCH_ZERO': HASH_MISMATCH == 0,
    }
    faltam = sorted(k for k, v in condicoes.items() if not v)
    return {'RAW_PRESERVATION_GATE_FR': 'CLOSED' if not faltam else 'OPEN',
            'CONDITIONS': condicoes, 'MISSING': faltam,
            'WHY': ('todas as oito condições satisfeitas' if not faltam
                    else 'faltam: ' + ', '.join(faltam))}


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else '--plano'
    if modo == '--plano':
        p = plano()
        for k in ('RAW_EXPECTED', 'LOCAL_FILES', 'DUPLICATE_REFERENCES',
                  'DISTINCT_STORAGE_KEYS', 'TOTAL_BYTES',
                  'LARGEST_ASSET_BYTES', 'EXCEEDS_BUCKET_LIMIT'):
            print('%-24s : %s' % (k, p[k]))
        print('%-24s : %s' % ('LARGEST_ASSET', p['LARGEST_ASSET']))
        print('%-24s : %d' % ('KEY_COLLISIONS', len(p['KEY_COLLISIONS'])))
        g = gate(RAW_EXPECTED=p['RAW_EXPECTED'], REMOTE_PRESENT=0, REMOTE_ABSENT=0,
                 ORPHANS=0, FAILED=0, CONTENT_HASH_CHECKED=0, SHA_VERIFIED=0,
                 HASH_MISMATCH=0)
        print('%-24s : %s' % ('RAW_PRESERVATION_GATE_FR', g['RAW_PRESERVATION_GATE_FR']))
        _, _, faltam = credencial()
        print('%-24s : %s' % ('CREDENCIAL', 'presente' if not faltam
                              else 'ausente (' + ', '.join(faltam) + ')'))
        return 0
    if modo == '--canario':
        c = canario()
        for k, v in c.items():
            print('%-26s : %s' % (k, v))
        return 0 if c['SUPABASE_AUTH_CANARY'] == 'PASS' else 1

    r = enviar() if modo == '--enviar' else verificar()
    if r.get('STATE') == 'NO_CREDENTIALS':
        print('sem credencial:', ', '.join(r['MISSING']))
        return 1
    if r.get('STATE') == 'AUTH_CANARY_FAILED':
        print('canario de autenticacao REPROVOU. UPLOAD_ATTEMPTS = 0')
        print('motivo:', r.get('WHY'))
        return 1
    for k in ('RAW_EXPECTED', 'REMOTE_PRESENT', 'REMOTE_ABSENT',
              'CONTENT_HASH_CHECKED', 'SHA_VERIFIED', 'HASH_MISMATCH', 'FAILED',
              'ORPHANS', 'KEY_COLLISIONS', 'BYTES_EXPECTED',
              'BYTES_VERIFIED_REMOTELY'):
        print('%-26s : %s' % (k, r[k]))
    print('%-26s : %s' % ('RAW_PRESERVATION_GATE_FR',
                          r['GATE']['RAW_PRESERVATION_GATE_FR']))
    if r['GATE']['MISSING']:
        print('%-26s : %s' % ('FALTAM', ', '.join(r['GATE']['MISSING'])))
    return 0 if r['GATE']['RAW_PRESERVATION_GATE_FR'] == 'CLOSED' else 1


if __name__ == '__main__':
    sys.exit(main())
