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
import re
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


def _proveniencia_por_arquivo():
    """arquivo local → TODAS as origens que apontam para ele.

    Um objeto pode ter mais de uma procedência, e guardar só a última apaga a
    outra. Medido: o rótulo ministerial do Highcard é linkado por DUAS páginas —
    a do próprio Highcard e a do sistema Max-Ace. A versão anterior deste código
    gravava só a segunda, e a página DONA do documento sumia do manifesto.

        MESMO CONTEÚDO ≠ MESMA PROCEDÊNCIA
    """
    fora = {}
    for nome in ('documentos-censo.json', 'documentos-amostra.json'):
        caminho = os.path.join(ACERVO, nome)
        if not os.path.exists(caminho):
            continue
        with open(caminho, encoding='utf-8') as fh:
            for d in json.load(fh).get('DOCUMENTS', []):
                if d.get('STATE') != 'DOWNLOADED' or not d.get('LOCAL_FILE'):
                    continue
                chave = os.path.basename(d['LOCAL_FILE'])
                linha = {'SOURCE_URL': d.get('SOURCE_URL'),
                         'ORIGINAL_FILENAME': d.get('ORIGINAL_FILENAME'),
                         'PRODUCT_PAGE': d.get('PRODUCT_URL'),
                         'PRODUCT_NAME': d.get('PRODUCT_NAME'),
                         'LABEL_ON_PAGE': d.get('LABEL_ON_PAGE'),
                         'CONTENT_SHA256': d.get('SHA256')}
                lista = fora.setdefault(chave, [])
                if linha not in lista:
                    lista.append(linha)
    return fora


def plano():
    """Assets a preservar, com hash RECALCULADO do disco agora.

    Não confia no manifesto: o manifesto diz o que foi baixado, o disco diz o que
    existe. Divergência entre os dois é achado, não detalhe.
    """
    proc = _proveniencia_por_arquivo()
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
            origens = proc.get(nome, [])
            itens.append({
                'ESPECIE': especie,
                'ARQUIVO_LOCAL': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
                'OBJETO': chave_de_storage(especie, sha, nome),
                'SHA256': sha, 'BYTES': n,
                'MEDIA_TYPE': _mime(caminho, mime_padrao),
                'ORIGINAL_FILENAME': (origens[0]['ORIGINAL_FILENAME']
                                      if origens else nome),
                'SOURCE_URL': origens[0]['SOURCE_URL'] if origens else None,
                'PRODUCT_URL': origens[0]['PRODUCT_PAGE'] if origens else None,
                'PROVENANCE': origens,
                'PROVENANCE_COUNT': len(origens),
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
            'PROVENANCE': [], 'PROVENANCE_COUNT': 0,
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
        'BYTES_EXPECTED': sum(i['BYTES'] for i in itens),
        'BYTES_TOTAIS': sum(i['BYTES'] for i in itens),
        'LARGEST_ASSET_BYTES': maior,

        # 141 links → 139 arquivos → 138 conteúdos. Nenhum dos três é erro, e a
        # relação entre eles fica escrita para ninguém confundir depois.
        'DOCUMENT_LINKS_TOTAL': sum(i['PROVENANCE_COUNT'] for i in itens),
        'OBJETOS_COM_MAIS_DE_UMA_ORIGEM': sum(1 for i in itens
                                              if i['PROVENANCE_COUNT'] > 1),
        'CONTEUDOS_DISTINTOS': len({i['SHA256'] for i in itens}),
        'OBJETOS_COM_CONTEUDO_REPETIDO': len(itens) - len({i['SHA256'] for i in itens}),
        'PORQUE_CONTEUDO_REPETIDO_NAO_E_ERRO': (
            'duas URLs podem servir os mesmos bytes, e duas páginas podem linkar o '
            'mesmo documento. A chave é endereçada por conteúdo, mas a PROCEDÊNCIA '
            'de cada link fica inteira em PROVENANCE — hash igual não apaga origem'),

        # §2 — a lista completa de documentos de cada produto está atrás de uma
        # rota que o robots.txt da própria ADAMA proíbe. Não foi aberta.
        'PRODUCT_CENSUS_COMPLETE': True,
        'DOCUMENT_CENSUS_COMPLETE': False,
        'DOCUMENT_CENSUS_INCOMPLETE_REASON': 'ROBOTS_DISALLOWS_AJAX_ROUTE',
        'DOCUMENT_CENSUS_NOTE': ('os documentos preservados são os que a página de '
                                 'produto mostra. O link "Tutti i documenti" leva a '
                                 '*/ajax/, proibido pelo robots.txt, e não foi aberto'),
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
# ─────────────────────────────────────────── formato da chave, e o cabeçalho
#
# A CICATRIZ: o Storage devolveu `Invalid Compact JWS` a TUDO, inclusive ao
# primeiro inventário. A causa não era permissão — era o cabeçalho.
#
# Este código mandava a MESMA chave nos dois lugares:
#
#     apikey: <chave>
#     Authorization: Bearer <chave>
#
# Isso funcionava enquanto a chave era a `service_role` antiga, porque ela É um
# JWT. As chaves novas do Supabase (`sb_secret_...`) são tokens opacos: não têm
# cabeçalho, corpo nem assinatura. O Storage extrai o `Authorization`, tira o
# "Bearer " e entrega a uma biblioteca JOSE, que rejeita a string antes de
# qualquer checagem de permissão — daí o 403 com `Invalid Compact JWS`.
#
#     SECRET KEY ≠ JWT
#
# Uma chave nova vai SÓ em `apikey`. Nunca em `Authorization: Bearer`.
NEW_SECRET_KEY = 'NEW_SECRET_KEY'
LEGACY_SERVICE_ROLE_JWT = 'LEGACY_SERVICE_ROLE_JWT'
UNKNOWN_KEY_FORMAT = 'UNKNOWN_KEY_FORMAT'

_RE_JWT = re.compile(r'^eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$')


def classificar_chave(key):
    """Formato pelo PREFIXO. Não decodifica, não transforma, não imprime.

    `sb_publishable_` e `anon` são recusadas de propósito: preservar exige
    escrita, e uma chave pública não escreve — falharia no meio do lote em vez
    de falhar antes dele.
    """
    k = (key or '').strip()
    if k.startswith('sb_secret_'):
        return NEW_SECRET_KEY
    if _RE_JWT.match(k):
        return LEGACY_SERVICE_ROLE_JWT
    return UNKNOWN_KEY_FORMAT


def cabecalhos(key, formato):
    """Os cabeçalhos de autenticação, por formato. Nunca os dois às cegas."""
    if formato == NEW_SECRET_KEY:
        return {'apikey': key}
    if formato == LEGACY_SERVICE_ROLE_JWT:
        return {'apikey': key, 'Authorization': 'Bearer ' + key}
    raise ValueError('formato de chave nao suportado: %s' % formato)


def sem_segredo(texto, key):
    """Nenhum caractere do segredo sai daqui — nem em erro, nem em log."""
    s = str(texto)
    if key:
        s = s.replace(key, '<OMITIDO>')
        for pedaco in (key[:12], key[-12:]):
            if len(pedaco) >= 8:
                s = s.replace(pedaco, '<OMITIDO>')
    return s


def autenticacao():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    key = os.environ.get('SUPABASE_SECRET_KEY', '')
    faltam = [n for n, v in (('SUPABASE_URL', url), ('SUPABASE_SECRET_KEY', key)) if not v]
    return url, key, faltam


def _http(url, key, metodo, caminho, dados=None, ctype=None, timeout=300,
          formato=None):
    cab = dict(cabecalhos(key, formato or classificar_chave(key)))
    if ctype:
        cab['Content-Type'] = ctype
    req = urllib.request.Request(url + caminho, data=dados, method=metodo, headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:                                   # rede caiu, DNS, TLS
        return 0, sem_segredo('%s: %s' % (type(e).__name__, e), key).encode()[:300]


# O 403 do Storage vem embrulhado num 400, e a palavra que importa está no corpo.
NEGA_AUTENTICACAO = re.compile(
    r'invalid compact jws|invalid jwt|bad_jwt|unauthorized|accessdenied|'
    r'invalid signature|jwt expired', re.I)


def canario(url, key, formato=None):
    """UMA leitura, e nada mais. Prova a autenticação sem tocar no Storage.

    Existe porque a rodada anterior descobriu o defeito de cabeçalho no meio do
    caminho. Uma leitura barata antes do lote transforma "falhou em algum lugar"
    em "não começou, e este é o motivo".
    """
    formato = formato or classificar_chave(key)
    st, body = _http(url, key, 'GET', '/storage/v1/bucket', formato=formato)
    texto = sem_segredo((body or b'').decode('utf-8', 'replace')[:400], key)
    base = {'KEY_FORMAT': formato, 'HTTP': st,
            'OPERACAO': 'GET /storage/v1/bucket — somente leitura'}
    if st == 200:
        try:
            nomes = [b.get('name') for b in json.loads(body)]
        except Exception:
            nomes = []
        return dict(base, AUTH_CANARY='PASS', BUCKETS_VISIVEIS=len(nomes),
                    BUCKET_ALVO_EXISTE=BUCKET in nomes)
    return dict(base, AUTH_CANARY='FAIL', MENSAGEM=texto,
                AUTENTICACAO_RECUSADA=bool(NEGA_AUTENTICACAO.search(texto))
                or st in (400, 401, 403),
                WHY='nenhum byte sobe enquanto a leitura não passar')


def inventario_remoto(url, key, prefixo=PREFIXO, formato=None):
    """O que o bucket diz que tem. A verdade do estado é o objeto remoto."""
    vistos, pilha = {}, [prefixo]
    while pilha:
        atual = pilha.pop()
        corpo = json.dumps({'prefix': atual, 'limit': 1000,
                            'sortBy': {'column': 'name', 'order': 'asc'}}).encode()
        st, body = _http(url, key, 'POST', '/storage/v1/object/list/' + BUCKET,
                         corpo, 'application/json', formato=formato)
        if st != 200:
            return None, sem_segredo('list %s devolveu HTTP %s: %s'
                                     % (atual, st, body[:160]), key)
        for o in json.loads(body):
            nome = '%s/%s' % (atual, o['name'])
            if o.get('id') is None:
                pilha.append(nome)
            else:
                vistos[nome] = (o.get('metadata') or {}).get('size')
    return vistos, None


class CanarioReprovado(RuntimeError):
    """Levantada ANTES de qualquer escrita. É a trava, não um aviso."""


def enviar(itens, url, key, verificar=True, formato=None, prova=None):
    """Sobe e confere. RECUSA começar se o canário não tiver passado.

    A trava é aqui, e não na `main`, porque quem chama a função de fora também
    tem de passar pela leitura. Sem prova de autenticação, zero PUT e zero POST.
    """
    if not prova or prova.get('AUTH_CANARY') != 'PASS':
        raise CanarioReprovado(
            'canário de leitura não passou (%s) — nenhum objeto foi enviado'
            % ((prova or {}).get('AUTH_CANARY') or 'NAO_EXECUTADO'))
    formato = formato or classificar_chave(key)
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
        st, body = _http(url, key, 'POST', alvo, corpo, it['MEDIA_TYPE'],
                         formato=formato)
        if st in (200, 201):
            it['ESTADO'] = 'UPLOADED'
        elif st == 409 or b'already exists' in body or b'Duplicate' in body:
            it['ESTADO'] = 'ALREADY_PRESENT'
        else:
            # HTTP_5XX ≠ OBJECT_NOT_PRESERVED — pergunta-se ao bucket antes de
            # carimbar falha.
            st2, volta = _http(url, key, 'GET', alvo, formato=formato)
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
            it['MOTIVO'] = sem_segredo(
                'upload devolveu HTTP %s: %s'
                % (st, body[:160].decode('utf-8', 'replace')), key)
            it['CONFERENCIA_REMOTA_APOS_FALHA'] = {'HTTP_NO_GET': st2,
                                                   'BYTES_DE_VOLTA': len(volta or b'')}
            continue
        if verificar:
            verificar_um(it, url, key, formato)
    return itens


def verificar_um(it, url, key, formato=None):
    """Baixa de volta e reconfere. É aqui que a preservação fecha."""
    alvo = '/storage/v1/object/%s/%s' % (BUCKET, urllib.parse.quote(it['OBJETO']))
    st, volta = _http(url, key, 'GET', alvo, formato=formato)
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
    bytes_esperados = sum(i.get('BYTES', 0) for i in itens)
    # Só conta byte que VOLTOU e bateu. Byte que subiu não é byte preservado.
    bytes_verificados = sum(i.get('BYTES_DE_VOLTA', 0) for i in itens
                            if i['ESTADO'] in VERIFICADOS)
    g = dict(rw.gate(esperado=esperado, remoto_presente=presentes,
                     remoto_ausente=esperado - presentes, orfaos=orfaos,
                     falhos=max(falhos, 0), hash_conferido=conferidos,
                     hash_divergente=divergentes),
             SHA_VERIFIED=verificados,
             BYTES_EXPECTED=bytes_esperados,
             BYTES_VERIFIED_REMOTELY=bytes_verificados,
             REMOTE_INVENTORY_READ=remoto is not None)
    # A oitava condição, e ela é de bytes: um objeto truncado passa por
    # "presente" e por "contado", e só não passa por aqui.
    g['CONDITIONS']['BYTES_VERIFIED_EQ_EXPECTED'] = (
        bytes_verificados == bytes_esperados)
    if not g['CONDITIONS']['BYTES_VERIFIED_EQ_EXPECTED']:
        g['MISSING'] = sorted(set(g['MISSING']) | {'BYTES_VERIFIED_EQ_EXPECTED'})
        g['STATE'] = 'OPEN'
        g['WHY'] = 'faltam: ' + ', '.join(g['MISSING'])
    return g


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

    formato = classificar_chave(key)
    print()
    print('KEY_FORMAT           :', formato)
    if formato == UNKNOWN_KEY_FORMAT:
        print('PARADO: formato de chave não reconhecido.')
        print('  esperado: sb_secret_... (chave nova) ou um JWT service_role.')
        print('  chave publicável e anon são recusadas: preservar exige escrita.')
        print('  nenhum caractere do segredo foi lido, decodificado ou impresso.')
        return 5

    # CANÁRIO: uma leitura, antes de qualquer byte. Se ela não passar, o lote
    # não começa — e o motivo fica escrito em vez de aparecer no meio do envio.
    prova = canario(url, key, formato)
    print('AUTH_CANARY          :', prova['AUTH_CANARY'], '(HTTP %s, %s)'
          % (prova['HTTP'], prova['OPERACAO']))
    if prova['AUTH_CANARY'] != 'PASS':
        print('  mensagem do servidor:', prova.get('MENSAGEM', '')[:200])
        print('  UPLOADS_ANTES_DO_CANARIO = 0 — nenhum byte foi enviado.')
        print('  RAW_PRESERVATION_GATE_IT continua OPEN.')
        return 6
    print('  bucket "%s" visível :' % BUCKET, prova.get('BUCKET_ALVO_EXISTE'))

    remoto, erro = inventario_remoto(url, key, formato=formato)
    if erro:
        print('inventário remoto falhou:', erro)
        remoto = None
    itens = p['ITENS']
    if '--enviar' in sys.argv:
        enviar(itens, url, key, formato=formato, prova=prova)
    else:
        for it in itens:
            verificar_um(it, url, key, formato)
    if remoto is None:
        remoto, _ = inventario_remoto(url, key, formato=formato)

    g = portao(itens, p['RAW_EXPECTED'], remoto)
    fechado = g['STATE'] == 'CLOSED'
    rel = {'SOURCE_ID': 'IT-ADAMA-CATALOG', 'source': p['source'],
           'captured_at': p['captured_at'], 'CAPTURED_AT': p['CAPTURED_AT'],
           'SOURCE_COUNTRY': 'IT', 'EVIDENCE_CLASS': 'PRESERVATION_PROOF',
           'PAIS': 'IT', 'RAW_EXPECTED': p['RAW_EXPECTED'],
           'PIPELINE': ['AUTH_CANARY', 'UPLOAD', 'INVENTORY', 'DOWNLOAD_BACK',
                        'SHA256', 'BYTE_COUNT'],
           'KEY_FORMAT': formato,
           'AUTH_CANARY': {k: v for k, v in prova.items() if k != 'MENSAGEM'},
           'PRESENCE_IN_BUCKET_IS_NOT_CONTENT_VERIFIED': True,
           'PRODUCT_CENSUS_COMPLETE': p['PRODUCT_CENSUS_COMPLETE'],
           'DOCUMENT_CENSUS_COMPLETE': p['DOCUMENT_CENSUS_COMPLETE'],
           'DOCUMENT_CENSUS_INCOMPLETE_REASON': p['DOCUMENT_CENSUS_INCOMPLETE_REASON'],
           'POR_ESTADO': _contar(itens, 'ESTADO'), 'GATE': g,
           'RAW_PRESERVATION_GATE_IT': 'CLOSED' if fechado else 'OPEN',
           'ADAMA_IT_PUBLIC_CATALOG_COMPLETE': (
               'YES_FOR_PRODUCTS / NO_FOR_ALL_DOCUMENTS_ROBOTS_RESTRICTION'),
           'ITALY_CATALOG_HANDOFF_READY': 'YES',
           'ITALY_LOCAL_FOUNDATION_CAPTURE': 'COMPLETE' if fechado else 'INCOMPLETE',
           'ITALY_DECISION_INTELLIGENCE_COMPLETE': (
               'NOT_DECLARED — captar a fundação e responder a pergunta de decisão '
               'são coisas diferentes, e só a primeira foi feita'),
           'NO_EAME_IMPORT': 'YES',
           'ITENS': itens}
    with open(RELATORIO, 'w', encoding='utf-8') as fh:
        json.dump(rel, fh, ensure_ascii=False, indent=2)
    print()
    print('por estado             :', rel['POR_ESTADO'])
    print('REMOTE_PRESENT         :', g['REMOTE_PRESENT'], '/', g['EXPECTED'])
    print('REMOTE_ABSENT          :', g['REMOTE_ABSENT'])
    print('CONTENT_HASH_CHECKED   :', g['CONTENT_HASH_CHECKED'])
    print('SHA_VERIFIED           :', g['SHA_VERIFIED'])
    print('HASH_MISMATCH          :', g['HASH_MISMATCH'])
    print('ORPHANS                :', g['ORPHANS'])
    print('FAILED                 :', g['FAILED'])
    print('BYTES_EXPECTED         :', g['BYTES_EXPECTED'])
    print('BYTES_VERIFIED_REMOTELY:', g['BYTES_VERIFIED_REMOTELY'])
    print('RAW_PRESERVATION_GATE_IT =', rel['RAW_PRESERVATION_GATE_IT'])
    if g['MISSING']:
        print('  faltam               :', ', '.join(g['MISSING']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
