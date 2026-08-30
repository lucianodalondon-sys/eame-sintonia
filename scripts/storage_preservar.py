#!/usr/bin/env python3
"""
PRESERVAÇÃO DOS BYTES — disco local -> Supabase Storage, com prova.

O problema que este arquivo resolve: os 296 MB de PDF e o RAW das páginas existem em UMA
máquina. Manifesto com sha256 não é backup. Enquanto os bytes não estiverem no Storage e
tiverem sido BAIXADOS DE VOLTA e reconferidos, a coleta é reversível por um formatador de
disco.

    python3 scripts/storage_preservar.py --plano            # offline, sempre roda
    python3 scripts/storage_preservar.py --provar-destino   # so leitura, nao envia
    python3 scripts/storage_preservar.py --diagnosticar     # inventario + UMA tentativa
    python3 scripts/storage_preservar.py --enviar           # exige autenticação
    python3 scripts/storage_preservar.py --enviar --so-falhos  # so o que falhou antes
    python3 scripts/storage_preservar.py --enviar --sem-verificar-hash

CONVENÇÃO — reusada, não inventada

Bucket `raw`, um para o EAME inteiro; o país vive no PATH (workflow supabase-storage.yml).
A chave dos documentos é a que o próprio parser já emite em STORAGE_KEY:

    ES/adama-website/<PRODUCT_ID>/<sha16>-<filename>

Ela é ENDEREÇADA POR CONTEÚDO: o sha16 entra no nome. Duas capturas do mesmo arquivo caem
no mesmo lugar; um arquivo que mudou cai em outro. Sobrescrita silenciosa de conteúdo
diferente deixa de ser possível pelo formato da chave.

    PATH != IDENTITY.  A identidade é run_id + sha256 + metadata, e mora em raw_asset.

AUTENTICAÇÃO

Só variável de ambiente já configurada: SUPABASE_URL e SUPABASE_SECRET_KEY — os mesmos
nomes que os workflows deste repo já usam. Este arquivo NÃO procura segredo em disco, não
lê .env, não imprime chave e não cria credencial. Sem as duas variáveis, `--enviar` recusa
e diz exatamente o que falta.

OS CINCO ESTADOS

    PENDING                    ainda não tentado
    UPLOADED                   subiu nesta execução
    ALREADY_PRESENT_VERIFIED   já estava lá, e os bytes de volta batem com o sha256 local
    VERIFIED                   subiu e os bytes de volta batem
    FAILED_WITH_REASON         não subiu, ou subiu e não bateu — com o motivo escrito

`preserved = true` só é escrito depois de VERIFIED ou ALREADY_PRESENT_VERIFIED. Nunca
depois de UPLOADED sozinho: HTTP 200 no upload diz que o servidor aceitou, não que os
bytes certos chegaram.
"""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
RAW = os.path.join(ROOT, 'data', 'raw', 'ES', 'adama-website')
BUCKET = 'raw'
PLANO = os.path.join(SAMPLES, 'ADAMA-ES-PRESERVACAO-PLANO.json')
RELATORIO = os.path.join(SAMPLES, 'ADAMA-ES-PRESERVACAO-RELATORIO.json')


# ══════════════════════════════════════════════════════════════════════════════
# 1 · O PLANO — o que preservar, medido do disco, sem rede
# ══════════════════════════════════════════════════════════════════════════════

def _sha_e_bytes(caminho):
    h = hashlib.sha256()
    n = 0
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b''):
            h.update(bloco)
            n += len(bloco)
    return h.hexdigest(), n


def plano():
    """Lista de assets a preservar, com hash RECALCULADO do arquivo agora.

    Não confia no manifesto: o manifesto diz o que foi baixado, o disco diz o que existe.
    Divergência entre os dois é achado, não detalhe — e sai como FAILED_WITH_REASON antes
    de qualquer byte subir.
    """
    itens, problemas = [], []

    # 1.1 · os documentos (PDF)
    idx = os.path.join(RAW, 'documentos-baixados.json')
    docs_por_media = {}
    if os.path.exists(idx):
        with open(idx, encoding='utf-8') as f:
            docs_por_media = json.load(f)

    artefato = os.path.join(SAMPLES, 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')
    chave_do_doc, captura_do_doc = {}, {}
    if os.path.exists(artefato):
        with open(artefato, encoding='utf-8') as f:
            art = json.load(f)
        for d in art.get('DOCUMENTS') or []:
            if d.get('DOWNLOAD_STATE') != 'DOWNLOADED':
                continue
            mid = _media_id(d.get('URL'))
            if mid:
                # STORAGE_KEY vem com o bucket na frente; o objeto é o resto.
                chave_do_doc[mid] = (d.get('STORAGE_KEY') or '').split('/', 1)[-1]
                captura_do_doc[mid] = d.get('CAPTURED_AT')

    for mid, d in sorted(docs_por_media.items(), key=lambda kv: int(kv[0])):
        caminho = os.path.join(RAW, 'documentos', d['ARQUIVO'])
        if not os.path.exists(caminho):
            problemas.append({'CLASSE': 'DOCUMENTO', 'MEDIA_ID': mid,
                              'ERRO': 'arquivo no manifesto e ausente no disco'})
            continue
        sha, n = _sha_e_bytes(caminho)
        if sha != d['SHA256'] or n != d['BYTES']:
            problemas.append({'CLASSE': 'DOCUMENTO', 'MEDIA_ID': mid,
                              'ERRO': 'disco diverge do manifesto',
                              'SHA_DISCO': sha, 'SHA_MANIFESTO': d['SHA256']})
            continue
        objeto = chave_do_doc.get(mid) or 'ES/adama-website/sem-produto/%s-%s' % (
            sha[:16], d['ARQUIVO'])
        itens.append({
            'CLASSE': 'DOCUMENTO', 'MEDIA_ID': mid,
            'ARQUIVO_LOCAL': os.path.relpath(caminho, ROOT).replace('\\', '/'),
            'OBJETO': objeto, 'MEDIA_TYPE': d.get('MIME') or 'application/pdf',
            'BYTES': n, 'SHA256': sha,
            'CAPTURADO_EM': captura_do_doc.get(mid) or d.get('CAPTURA_UTC'),
            'SOURCE_URL': 'https://www.adama.com/spain/es/media/%s/download?attachment' % mid,
            'ESTADO': 'PENDING',
        })

    # 1.2 · o RAW das páginas de produto
    manp = os.path.join(RAW, 'manifest-paginas.json')
    if os.path.exists(manp):
        with open(manp, encoding='utf-8') as f:
            for r in json.load(f):
                caminho = os.path.join(ROOT, r['ARQUIVO'].replace('/', os.sep))
                if not os.path.exists(caminho):
                    problemas.append({'CLASSE': 'PAGINA', 'URL': r['URL'],
                                      'ERRO': 'html no manifesto e ausente no disco'})
                    continue
                sha, n = _sha_e_bytes(caminho)
                if sha != r['SHA256']:
                    problemas.append({'CLASSE': 'PAGINA', 'URL': r['URL'],
                                      'ERRO': 'disco diverge do manifesto'})
                    continue
                nome = os.path.basename(caminho)
                itens.append({
                    'CLASSE': 'PAGINA', 'URL': r['URL'],
                    'ARQUIVO_LOCAL': r['ARQUIVO'],
                    'OBJETO': 'ES/adama-website/paginas/%s-%s' % (sha[:16], nome),
                    'MEDIA_TYPE': 'text/html; charset=utf-8',
                    'BYTES': n, 'SHA256': sha,
                    'CAPTURADO_EM': None, 'SOURCE_URL': r['URL'], 'ESTADO': 'PENDING',
                })

    # 1.3 · os pacotes de captura — sem eles o censo não se reproduz
    for nome in ('ADAMA-ES-PACOTE-PAGINAS.json', 'ADAMA-ES-PACOTE-CATALOGO.json'):
        caminho = os.path.join(RAW, nome)
        if not os.path.exists(caminho):
            problemas.append({'CLASSE': 'PACOTE', 'ARQUIVO': nome, 'ERRO': 'ausente no disco'})
            continue
        sha, n = _sha_e_bytes(caminho)
        with open(caminho, encoding='utf-8') as f:
            cap = json.load(f).get('CAPTURA_UTC')
        itens.append({
            'CLASSE': 'PACOTE', 'ARQUIVO_LOCAL': 'data/raw/ES/adama-website/' + nome,
            'OBJETO': 'ES/adama-website/pacotes/%s-%s' % (sha[:16], nome),
            'MEDIA_TYPE': 'application/json', 'BYTES': n, 'SHA256': sha,
            'CAPTURADO_EM': cap, 'SOURCE_URL': 'https://www.adama.com/spain/es/',
            'ESTADO': 'PENDING',
        })

    # A data de captura do plano é a da CAPTURA dos bytes, não a de hoje: o plano fala
    # sobre arquivos que foram lidos do site naquele momento. Sem ela, o guarda de
    # proveniência barra o artefato — e barra com razão.
    capturas = sorted({i['CAPTURADO_EM'] for i in itens if i.get('CAPTURADO_EM')})

    return {
        'SOURCE_ID': 'ADAMA-ES-PRESERVACAO-PLANO',
        'source': 'bytes capturados do site publico da ADAMA Espana, no disco local',
        'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN', 'ORIGINAL_LANGUAGE': 'ES',
        'captured_at': (capturas[0] if capturas else 'NOT_COLLECTED'),
        'CAPTURE_DATE': (capturas[0] if capturas else 'NOT_COLLECTED'),
        'CAPTURA_MAIS_RECENTE': (capturas[-1] if capturas else 'NOT_COLLECTED'),
        'COUNTRY': 'ES',
        'BUCKET': BUCKET,
        'CONVENCAO_DE_CHAVE': 'ES/adama-website/... — endereçada por conteúdo (sha16 no nome)',
        'ITENS': len(itens),
        'BYTES': sum(i['BYTES'] for i in itens),
        'POR_CLASSE': _contar(itens, 'CLASSE'),
        'PROBLEMAS_ANTES_DE_ENVIAR': problemas,
        'LEI': ('manifesto != bytes preservados. Este arquivo é o plano; preservado só '
                'depois de baixar de volta e reconferir o sha256.'),
        'ASSETS': itens,
    }


_RX_MEDIA = re.compile(r'/media/(\d+)/download', re.I)


def _media_id(url):
    m = _RX_MEDIA.search(url or '')
    return m.group(1) if m else None


def _contar(itens, campo):
    fora = {}
    for i in itens:
        fora[i[campo]] = fora.get(i[campo], 0) + 1
    return fora


# ══════════════════════════════════════════════════════════════════════════════
# 2 · O ENVIO — só com autenticação já configurada no ambiente
# ══════════════════════════════════════════════════════════════════════════════

def autenticacao():
    """(disponivel, o_que_falta). NUNCA devolve nem imprime o valor da chave."""
    url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
    key = (os.environ.get('SUPABASE_SECRET_KEY') or '').strip()
    falta = [n for n, v in (('SUPABASE_URL', url), ('SUPABASE_SECRET_KEY', key)) if not v]
    return (not falta), falta, url, key


def _http(url, key, metodo, caminho, dados=None, ctype=None, timeout=300, detalhe=None):
    """Se `detalhe` for um dict, recebe status, content-type e CORPO SANITIZADO.

    Guardar só "HTTP 400" foi insuficiente: 400 pode ser chave inválida, caminho
    inválido, tamanho, mime, ou objeto já existente, e cada um pede uma correção
    diferente. Adivinhar pelo número é o mesmo erro de tratar falha como ausência.
    """
    cab = {'apikey': key, 'Authorization': 'Bearer ' + key}
    if ctype:
        cab['Content-Type'] = ctype
    req = urllib.request.Request(url + caminho, data=dados, method=metodo, headers=cab)

    def _registrar(status, corpo, headers=None):
        if detalhe is None:
            return
        detalhe.update({
            'HTTP_STATUS': status,
            'RESPONSE_CONTENT_TYPE': (headers or {}).get('Content-Type', 'NÃO SEI'),
            'RESPONSE_BODY_SANITIZED': _sanitizar(corpo, key),
            # O caminho vai SEM host: o host nao e segredo, mas tambem nao acrescenta
            # nada ao diagnostico, e caminho curto e mais facil de comparar.
            'REQUEST_OBJECT_PATH': caminho,
        })

    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            corpo = r.read()
            _registrar(r.status, corpo, dict(r.headers))
            return r.status, corpo
    except urllib.error.HTTPError as e:
        corpo = e.read()
        _registrar(e.code, corpo, dict(e.headers or {}))
        return e.code, corpo
    except Exception as e:                                        # noqa: BLE001
        corpo = ('%s: %s' % (type(e).__name__, e)).encode()
        _registrar(0, corpo)
        return 0, corpo


_RX_JWT = re.compile(r'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}')


def _sanitizar(corpo, key):
    """Corpo da resposta legível, sem chave dentro.

    O Supabase não costuma devolver a credencial, mas "não costuma" não é garantia, e
    este texto vai para um artefato versionado. Três redações: a chave em uso, qualquer
    coisa com forma de JWT, e os cabeçalhos de autenticação por nome.
    """
    try:
        txt = corpo.decode('utf-8', 'replace')
    except Exception:                                             # noqa: BLE001
        return '<%d bytes nao textuais>' % len(corpo or b'')
    if key:
        txt = txt.replace(key, '<CHAVE_OMITIDA>')
    txt = _RX_JWT.sub('<JWT_OMITIDO>', txt)
    for nome in ('apikey', 'Authorization', 'service_role', 'SUPABASE_SECRET_KEY'):
        txt = re.sub(r'(?i)(%s)\s*[:=]\s*\S+' % re.escape(nome), r'\1=<OMITIDO>', txt)
    return txt[:1200]


def bucket_esta_certo(url, key):
    """O bucket `raw` existe e é PRIVADO? Público seria vazamento de evidência.

    FALHA NÃO É AUSÊNCIA — e esta função já quebrou essa lei uma vez.

    A versão anterior perguntava GET /storage/v1/bucket/raw e devolvia EXISTE=False para
    QUALQUER coisa que não fosse 200. Em 2026-08-30 isso fez o uploader dizer "bucket
    ausente — criar antes" sobre um bucket que existia desde 2026-08-29, criado e
    verificado pelo próprio workflow canônico. Três causas diferentes saíam com a mesma
    frase: bucket inexistente, chave sem permissão, e projeto errado.

    Agora usa a MESMA leitura do workflow (lista de buckets) e devolve o estado medido:

        EXISTE=True                     'raw' está na lista
        EXISTE=False                    a lista veio e 'raw' NÃO está nela — ausência real
        EXISTE='NAO_SEI' + NAO_AUTORIZADO   401/403: a chave não pode listar bucket.
                                        Chave publishable/anon não lista; só a secret.
        EXISTE='NAO_SEI' + HTTP <code>  qualquer outra resposta, com o código medido
    """
    st, body = _http(url, key, 'GET', '/storage/v1/bucket')
    if st in (401, 403):
        return {'EXISTE': 'NAO_SEI', 'PRIVADO': None, 'HTTP': st,
                'PORQUE': ('a chave nao tem permissao para listar buckets. Uma chave '
                           'publishable/anon nunca lista; o Storage exige a secret. '
                           'Isto NAO diz que o bucket falta.')}
    if st != 200:
        return {'EXISTE': 'NAO_SEI', 'PRIVADO': None, 'HTTP': st,
                'PORQUE': ('a listagem de buckets devolveu HTTP %s. Sem lista nao da '
                           'para afirmar presenca nem ausencia.' % st)}
    try:
        buckets = json.loads(body)
        nomes = [b.get('name') for b in buckets]
    except (ValueError, AttributeError, TypeError):
        return {'EXISTE': 'NAO_SEI', 'PRIVADO': None, 'HTTP': st,
                'PORQUE': 'a resposta veio 200 mas nao e a lista de buckets esperada'}
    raw = next((b for b in buckets if b.get('name') == BUCKET), None)
    if raw is None:
        return {'EXISTE': False, 'PRIVADO': None, 'HTTP': st, 'BUCKETS': nomes,
                'PORQUE': ('a lista respondeu e nao tem `%s`. Se o workflow canonico ja '
                           'criou, entao esta chave aponta para OUTRO projeto.' % BUCKET)}
    return {'EXISTE': True, 'PRIVADO': not raw.get('public', False), 'HTTP': st,
            'BUCKETS': nomes, 'DETALHE': {'id': raw.get('id'),
                                          'file_size_limit': raw.get('file_size_limit'),
                                          'allowed_mime_types': raw.get('allowed_mime_types')}}


def inventario_remoto(url, key, prefixo='ES/adama-website'):
    """Lista TUDO que já está no bucket sob o prefixo. Só leitura, paginada.

    Serve a duas perguntas que o relatório de envio não responde: quantos objetos
    realmente existem lá (independente do que o relatório diz que aconteceu), e se
    alguma tentativa antiga deixou objeto órfão. A API lista uma pasta por vez, então
    desce recursivamente — objeto sem barra é arquivo, com barra é pasta.
    """
    encontrados, pilha, erros = {}, [prefixo], []
    while pilha:
        pasta = pilha.pop()
        desloc = 0
        while True:
            corpo = json.dumps({'prefix': pasta, 'limit': 1000, 'offset': desloc}).encode()
            st, body = _http(url, key, 'POST', '/storage/v1/object/list/' + BUCKET,
                             corpo, 'application/json')
            if st != 200:
                erros.append({'PASTA': pasta, 'HTTP': st,
                              'CORPO': _sanitizar(body, key)[:200]})
                break
            try:
                itens = json.loads(body)
            except ValueError:
                erros.append({'PASTA': pasta, 'HTTP': st, 'CORPO': 'resposta nao-JSON'})
                break
            if not itens:
                break
            for it in itens:
                nome = it.get('name')
                if not nome:
                    continue
                caminho = (pasta + '/' + nome) if pasta else nome
                # `id` nulo é como a API marca PASTA; arquivo real traz metadata.
                if it.get('id') is None and not (it.get('metadata') or {}).get('size'):
                    pilha.append(caminho)
                else:
                    encontrados[caminho] = (it.get('metadata') or {}).get('size')
            if len(itens) < 1000:
                break
            desloc += len(itens)
    return encontrados, erros


def diagnosticar_um(item, url, key):
    """UMA tentativa, com o corpo real capturado. Não altera nada além desse objeto."""
    caminho_local = os.path.join(ROOT, item['ARQUIVO_LOCAL'].replace('/', os.sep))
    sha, n = _sha_e_bytes(caminho_local)
    prova_local = {
        'ARQUIVO_LOCAL': item['ARQUIVO_LOCAL'],
        'EXISTE_NO_DISCO': True,
        'BYTES_MEDIDOS': n, 'BYTES_ESPERADOS': item['BYTES'],
        'SHA256_MEDIDO': sha, 'SHA256_ESPERADO': item['SHA256'],
        'SHA_CONFERE': sha == item['SHA256'] and n == item['BYTES'],
    }
    with open(caminho_local, 'rb') as f:
        corpo = f.read()
    alvo = '/storage/v1/object/%s/%s' % (BUCKET, urllib.parse.quote(item['OBJETO']))
    detalhe = {}
    _http(url, key, 'POST', alvo, corpo, item['MEDIA_TYPE'], detalhe=detalhe)
    return {'PROVA_LOCAL': prova_local,
            'OBJETO': item['OBJETO'],
            'OBJETO_URL_ENCODED': urllib.parse.quote(item['OBJETO']),
            'CARACTERES_NAO_ASCII': sorted({c for c in item['OBJETO'] if ord(c) > 127}),
            'RESPOSTA': detalhe}


def preservar(itens, url, key, verificar_hash=True):
    """Sobe e CONFERE. Devolve os itens com ESTADO final e o motivo quando falha."""
    for it in itens:
        caminho = os.path.join(ROOT, it['ARQUIVO_LOCAL'].replace('/', os.sep))
        try:
            with open(caminho, 'rb') as f:
                corpo = f.read()
        except OSError as e:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'nao consegui ler o arquivo local: %s' % type(e).__name__
            continue

        # confere de novo, contra os bytes que vão de fato subir
        sha = hashlib.sha256(corpo).hexdigest()
        if sha != it['SHA256'] or len(corpo) != it['BYTES']:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'o arquivo mudou entre o plano e o envio'
            continue

        alvo = '/storage/v1/object/%s/%s' % (BUCKET, urllib.parse.quote(it['OBJETO']))
        detalhe = {}
        st, body = _http(url, key, 'POST', alvo, corpo, it['MEDIA_TYPE'], detalhe=detalhe)
        ja_existia = st == 409 or b'already exists' in body or b'Duplicate' in body
        if st in (200, 201):
            it['ESTADO'] = 'UPLOADED'
        elif ja_existia:
            it['ESTADO'] = 'ALREADY_PRESENT'
        else:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            # O motivo carrega o CORPO, não só o número. "HTTP 400" sozinho não diz se a
            # correção é no nome do objeto, no tamanho, no mime ou em outro lugar.
            it['MOTIVO'] = 'upload devolveu HTTP %s' % st
            it['DIAGNOSTICO'] = detalhe
            continue

        if not verificar_hash:
            it['VERIFICACAO'] = 'NAO_EXECUTADA'
            continue

        st, volta = _http(url, key, 'GET', alvo)
        if st != 200:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'objeto nao voltou para conferencia: HTTP %s' % st
            continue
        if hashlib.sha256(volta).hexdigest() != it['SHA256'] or len(volta) != it['BYTES']:
            # A chave carrega o sha16, então isto quer dizer colisão real ou corrupção.
            # Em nenhum dos dois casos se sobrescreve: para e reporta.
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = ('os bytes de volta NAO batem com o sha256 local — nao '
                            'sobrescrevi; conteudo diferente no mesmo caminho')
            continue
        it['ESTADO'] = ('ALREADY_PRESENT_VERIFIED' if it['ESTADO'] == 'ALREADY_PRESENT'
                        else 'VERIFIED')
        it['VERIFICACAO'] = 'SHA256_DEPOIS_DE_BAIXAR_DE_VOLTA'
    return itens


def resumo(itens, capturado_em=None):
    est = _contar(itens, 'ESTADO')
    preservados = [i for i in itens
                   if i['ESTADO'] in ('VERIFIED', 'ALREADY_PRESENT_VERIFIED')]
    capturas = sorted({i['CAPTURADO_EM'] for i in itens if i.get('CAPTURADO_EM')})
    return {
        # O relatório é amostra publicada e precisa do envelope, como qualquer outra.
        # Nasceu sem, e três guardas de proveniência do repo pegaram — com razão.
        'SOURCE_ID': 'ADAMA-ES-PRESERVACAO-RELATORIO',
        'source': 'envio dos bytes capturados para o Supabase Storage, bucket raw',
        'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN', 'ORIGINAL_LANGUAGE': 'ES',
        'COUNTRY': 'ES',
        'captured_at': capturado_em or (capturas[0] if capturas else 'NOT_COLLECTED'),
        'CAPTURE_DATE': capturado_em or (capturas[0] if capturas else 'NOT_COLLECTED'),
        'ASSETS_ESPERADOS': len(itens),
        'POR_ESTADO': est,
        'PRESERVADOS_E_VERIFICADOS': len(preservados),
        'FALHOS': est.get('FAILED_WITH_REASON', 0),
        'BYTES_LOCAIS': sum(i['BYTES'] for i in itens),
        'BYTES_VERIFICADOS': sum(i['BYTES'] for i in preservados),
        'HASH_MISMATCH': sum(1 for i in itens
                             if i['ESTADO'] == 'FAILED_WITH_REASON'
                             and 'NAO batem' in (i.get('MOTIVO') or '')),
        'LEI': ('preserved=true so para VERIFIED e ALREADY_PRESENT_VERIFIED. HTTP 200 no '
                'upload diz que o servidor aceitou, nao que os bytes certos chegaram.'),
    }


if __name__ == '__main__':
    p = plano()
    if '--plano' in sys.argv:
        with open(PLANO, 'w', encoding='utf-8') as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
        print('PLANO %s' % os.path.relpath(PLANO, ROOT))
        print('  ITENS=%d BYTES=%d POR_CLASSE=%s' % (p['ITENS'], p['BYTES'], p['POR_CLASSE']))
        print('  PROBLEMAS=%d' % len(p['PROBLEMAS_ANTES_DE_ENVIAR']))
        sys.exit(0)

    if '--diagnosticar' in sys.argv:
        # Inventário remoto (só leitura) + UMA tentativa isolada, com o corpo capturado.
        # Não reenvia os já preservados e não mexe em mais nada.
        ok, falta, url, key = autenticacao()
        if not ok:
            print('STORAGE_AUTH_MISSING')
            print('FALTA=' + ','.join(falta))
            sys.exit(2)

        remoto, erros = inventario_remoto(url, key)
        por_objeto = {a['OBJETO']: a for a in p['ASSETS']}
        presentes = [o for o in por_objeto if o in remoto]
        ausentes = [o for o in por_objeto if o not in remoto]
        orfaos = [o for o in remoto if o not in por_objeto]
        print('INVENTARIO_REMOTO_OBJETOS=%d' % len(remoto))
        print('DO_PLANO_PRESENTES=%d' % len(presentes))
        print('DO_PLANO_AUSENTES=%d' % len(ausentes))
        print('ORFAOS_NO_BUCKET=%d' % len(orfaos))
        if erros:
            print('ERROS_DE_LISTAGEM=%s' % erros[:3])
        for o in orfaos[:10]:
            print('  ORFAO: %s' % o)

        # Qual asset diagnosticar: o pedido, ou o MENOR ausente — menor é mais barato e
        # o tamanho não muda a natureza de um erro de nome.
        pedido = None
        i = sys.argv.index('--diagnosticar')
        if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith('-'):
            pedido = sys.argv[i + 1]
        alvos = [por_objeto[o] for o in ausentes]
        if pedido:
            alvos = [a for a in alvos if str(a.get('MEDIA_ID')) == pedido] or alvos
        if not alvos:
            print('NADA_A_DIAGNOSTICAR — todo objeto do plano ja esta no bucket')
            sys.exit(0)
        alvo = min(alvos, key=lambda a: a['BYTES'])
        print('\nDIAGNOSTICO_DE=%s (%s, %d bytes)'
              % (alvo.get('MEDIA_ID'), alvo['CLASSE'], alvo['BYTES']))
        d = diagnosticar_um(alvo, url, key)
        print(json.dumps(d, ensure_ascii=False, indent=1))
        caminho = os.path.join(SAMPLES, 'ADAMA-ES-PRESERVACAO-DIAGNOSTICO.json')
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump({'SOURCE_ID': 'ADAMA-ES-PRESERVACAO-DIAGNOSTICO',
                       'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN',
                       'captured_at': p.get('captured_at'),
                       'INVENTARIO_REMOTO_OBJETOS': len(remoto),
                       'DO_PLANO_PRESENTES': len(presentes),
                       'DO_PLANO_AUSENTES': sorted(ausentes),
                       'ORFAOS_NO_BUCKET': sorted(orfaos),
                       'ERROS_DE_LISTAGEM': erros,
                       'TENTATIVA': d}, f, ensure_ascii=False, indent=1)
        print('\nescrito em %s' % os.path.relpath(caminho, ROOT))
        sys.exit(0)

    if '--provar-destino' in sys.argv:
        # SÓ LEITURA. Não envia, não cria bucket, não muda nada. Existe porque "o bucket
        # existe?" é uma pergunta que merece resposta sozinha, antes de qualquer byte.
        ok, falta, url, key = autenticacao()
        if not ok:
            print('STORAGE_AUTH_MISSING')
            print('FALTA=' + ','.join(falta))
            sys.exit(2)
        st, _ = _http(url, key, 'GET', '/rest/v1/')
        print('PROJECT_REACHABLE=%s (HTTP %s)' % ('YES' if st == 200 else 'NO', st))
        b = bucket_esta_certo(url, key)
        print('RAW_BUCKET_EXISTS=%s' % b['EXISTE'])
        print('RAW_BUCKET_PRIVATE=%s' % b['PRIVADO'])
        print('HTTP=%s' % b['HTTP'])
        if b.get('BUCKETS') is not None:
            print('BUCKETS_VISIVEIS=%s' % b['BUCKETS'])
        if b.get('DETALHE'):
            print('DETALHE=%s' % b['DETALHE'])
        if b.get('PORQUE'):
            print('PORQUE=%s' % b['PORQUE'])
        print('NADA FOI ENVIADO — este modo so le.')
        sys.exit(0 if b['EXISTE'] is True else 1)

    if '--enviar' in sys.argv:
        ok, falta, url, key = autenticacao()
        if not ok:
            print('SUPABASE_AUTH_AVAILABLE=NO')
            print('FALTA=' + ','.join(falta))
            print('NADA FOI ENVIADO. O plano local esta completo e conferido; o unico')
            print('bloqueio e a autenticacao. Exporte as duas variaveis e rode de novo.')
            sys.exit(2)
        b = bucket_esta_certo(url, key)
        print('RAW_BUCKET_EXISTS=%s RAW_BUCKET_PRIVATE=%s HTTP=%s'
              % (b['EXISTE'], b['PRIVADO'], b['HTTP']))
        if b.get('BUCKETS') is not None:
            print('BUCKETS_VISIVEIS=%s' % b['BUCKETS'])
        if b.get('PORQUE'):
            print('PORQUE=%s' % b['PORQUE'])
        # Os tres desfechos ruins são DIFERENTES e saem com codigos diferentes: o operador
        # precisa saber se cria bucket, se troca a chave, ou se conferiu o projeto errado.
        if b['EXISTE'] == 'NAO_SEI':
            print('NAO_SEI se o bucket existe — nao afirmo ausencia sobre uma leitura que')
            print('nao respondeu. Isto NAO e motivo para criar bucket.')
            sys.exit(5)
        if b['EXISTE'] is False:
            print('bucket `raw` AUSENTE nesta chave — criar pelo workflow canonico')
            print('(.github/workflows/supabase-storage.yml). Se ele ja rodou com sucesso,')
            print('entao esta chave aponta para outro projeto: confira antes de criar.')
            sys.exit(3)
        if b['PRIVADO'] is False:
            print('bucket `raw` esta PUBLICO — recuso enviar evidencia para bucket publico')
            sys.exit(4)
        # --so-falhos trabalha SOMENTE sobre o que falhou na rodada anterior. Os já
        # verificados não são reenviados: não há segundo upload, não há segundo objeto.
        alvos = p['ASSETS']
        anterior = None
        if os.path.exists(RELATORIO):
            with open(RELATORIO, encoding='utf-8') as f:
                anterior = json.load(f)
        if '--so-falhos' in sys.argv:
            if not anterior:
                print('sem relatorio anterior — nao sei quais foram os falhos')
                sys.exit(6)
            falhos = {a['OBJETO'] for a in anterior['ASSETS']
                      if a['ESTADO'] == 'FAILED_WITH_REASON'}
            alvos = [a for a in p['ASSETS'] if a['OBJETO'] in falhos]
            print('MODO=SO_FALHOS  alvos=%d  intocados=%d'
                  % (len(alvos), len(p['ASSETS']) - len(alvos)))

        itens = preservar(alvos, url, key,
                          verificar_hash='--sem-verificar-hash' not in sys.argv)

        # Quem não foi alvo mantém o estado que JÁ tinha, medido antes. Não se inventa
        # estado para item que esta execução não tocou.
        if len(alvos) != len(p['ASSETS']):
            por_objeto = {a['OBJETO']: a for a in itens}
            for a in anterior['ASSETS']:
                if a['OBJETO'] not in por_objeto:
                    por_objeto[a['OBJETO']] = dict(a, TOCADO_NESTA_EXECUCAO=False)
            itens = [por_objeto[a['OBJETO']] for a in p['ASSETS']
                     if a['OBJETO'] in por_objeto]

        r = dict(resumo(itens, p.get('captured_at')), BUCKET=BUCKET, ASSETS=itens)

        # O relatório anterior NÃO é sobrescrito em silêncio. A segunda execução apagou a
        # primeira, e com ela a resposta de "qual asset mudou de estado entre as duas" —
        # a pergunta ficou sem dado, não sem importância. Agora fica a comparação.
        if anterior:
            antes = {a['OBJETO']: a['ESTADO'] for a in anterior['ASSETS']}
            mudou = [{'OBJETO': a['OBJETO'], 'DE': antes.get(a['OBJETO'], 'AUSENTE'),
                      'PARA': a['ESTADO'], 'MOTIVO': a.get('MOTIVO')}
                     for a in itens if antes.get(a['OBJETO']) != a['ESTADO']]
            r['MUDANCA_DESDE_A_EXECUCAO_ANTERIOR'] = mudou
            r['RESUMO_ANTERIOR'] = {k: anterior.get(k) for k in
                                    ('PRESERVADOS_E_VERIFICADOS', 'FALHOS', 'POR_ESTADO')}
            with open(RELATORIO.replace('.json', '-ANTERIOR.json'), 'w',
                      encoding='utf-8') as f:
                json.dump(anterior, f, ensure_ascii=False, indent=1)
            for m in mudou:
                print('MUDOU %s: %s -> %s' % (m['OBJETO'].split('/')[-1], m['DE'], m['PARA']))

        with open(RELATORIO, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        for k in ('ASSETS_ESPERADOS', 'PRESERVADOS_E_VERIFICADOS', 'FALHOS',
                  'HASH_MISMATCH', 'POR_ESTADO'):
            print('%s=%s' % (k, r[k]))
        sys.exit(1 if r['FALHOS'] else 0)

    print(__doc__)
