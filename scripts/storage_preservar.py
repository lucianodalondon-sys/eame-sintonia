#!/usr/bin/env python3
"""
PRESERVAÇÃO DOS BYTES — disco local -> Supabase Storage, com prova.

O problema que este arquivo resolve: os 296 MB de PDF e o RAW das páginas existem em UMA
máquina. Manifesto com sha256 não é backup. Enquanto os bytes não estiverem no Storage e
tiverem sido BAIXADOS DE VOLTA e reconferidos, a coleta é reversível por um formatador de
disco.

    python3 scripts/storage_preservar.py --plano            # offline, sempre roda
    python3 scripts/storage_preservar.py --enviar           # exige autenticação
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


_RX_MEDIA = None


def _media_id(url):
    global _RX_MEDIA
    if _RX_MEDIA is None:
        import re
        _RX_MEDIA = re.compile(r'/media/(\d+)/download', re.I)
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
    except Exception as e:                                        # noqa: BLE001
        return 0, ('%s: %s' % (type(e).__name__, e)).encode()


def bucket_esta_certo(url, key):
    """O bucket `raw` existe e é PRIVADO? Público seria vazamento de evidência."""
    st, body = _http(url, key, 'GET', '/storage/v1/bucket/' + BUCKET)
    if st != 200:
        return {'EXISTE': False, 'PRIVADO': None, 'HTTP': st}
    try:
        d = json.loads(body)
    except ValueError:
        return {'EXISTE': True, 'PRIVADO': None, 'HTTP': st}
    return {'EXISTE': True, 'PRIVADO': not d.get('public', False), 'HTTP': st}


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
        st, body = _http(url, key, 'POST', alvo, corpo, it['MEDIA_TYPE'])
        ja_existia = st == 409 or b'already exists' in body or b'Duplicate' in body
        if st in (200, 201):
            it['ESTADO'] = 'UPLOADED'
        elif ja_existia:
            it['ESTADO'] = 'ALREADY_PRESENT'
        else:
            it['ESTADO'] = 'FAILED_WITH_REASON'
            it['MOTIVO'] = 'upload devolveu HTTP %s' % st
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


def resumo(itens):
    est = _contar(itens, 'ESTADO')
    preservados = [i for i in itens
                   if i['ESTADO'] in ('VERIFIED', 'ALREADY_PRESENT_VERIFIED')]
    return {
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

    if '--enviar' in sys.argv:
        ok, falta, url, key = autenticacao()
        if not ok:
            print('SUPABASE_AUTH_AVAILABLE=NO')
            print('FALTA=' + ','.join(falta))
            print('NADA FOI ENVIADO. O plano local esta completo e conferido; o unico')
            print('bloqueio e a autenticacao. Exporte as duas variaveis e rode de novo.')
            sys.exit(2)
        b = bucket_esta_certo(url, key)
        print('RAW_BUCKET_EXISTS=%s RAW_BUCKET_PRIVATE=%s' % (b['EXISTE'], b['PRIVADO']))
        if not b['EXISTE']:
            print('bucket `raw` ausente — criar antes (workflow supabase-storage.yml)')
            sys.exit(3)
        if b['PRIVADO'] is False:
            print('bucket `raw` esta PUBLICO — recuso enviar evidencia para bucket publico')
            sys.exit(4)
        itens = preservar(p['ASSETS'], url, key,
                          verificar_hash='--sem-verificar-hash' not in sys.argv)
        r = dict(resumo(itens), BUCKET=BUCKET, ASSETS=itens)
        with open(RELATORIO, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        for k in ('ASSETS_ESPERADOS', 'PRESERVADOS_E_VERIFICADOS', 'FALHOS',
                  'HASH_MISMATCH', 'POR_ESTADO'):
            print('%s=%s' % (k, r[k]))
        sys.exit(1 if r['FALHOS'] else 0)

    print(__doc__)
