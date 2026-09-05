#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconcilia os 195 objetos do prefixo IT/adama-website do bucket `raw` contra o acervo
inteiro da casa — e para na porta da Inteligência.

O QUE ESTE SCRIPT NÃO É
    Não é coleta. Não fala com o Supabase, não fala com adama.com, não abre a rede, não
    escreve no Storage e não ativa o Passaporte. Ele responde UMA pergunta:

        de cada um dos 195 objetos que já estão no balde, o que a casa já sabe?

    A pergunta que ele NÃO responde é "o que cada objeto deveria ter virado". Essa é da
    Inteligência, e a Inteligência começa depois do último `print` daqui.

POR QUE ELE LÊ O GIT, E NÃO O BALDE
    Não há `SUPABASE_URL` nem `SUPABASE_SECRET_KEY` neste ambiente — e a rota até o balde
    já tinha sido tentada e registrada como fechada aqui, em LABEL-MANIFEST.json:
    `SUPABASE_BUCKET → NO_CREDENTIALS_IN_THIS_ENVIRONMENT`. O inventário dos 195 já existe
    em Git, com SHA256 conferido depois do download de volta. Reconciliar contra a prova
    preservada é a rota barata; abrir o balde não acrescentaria um fato e custaria uma
    credencial que este ambiente não deve ter.

AS TRÊS LEIS QUE ESTE CÓDIGO OBEDECE
    1. MENCIONADO NÃO É CONSUMIDO. Um objeto aparecer numa pasta de inteligência não prova
       nada sobre ele. `CONSUMED` exige duas provas citadas: o conteúdo foi lido E virou
       fato derivado.
    2. CHAVE FRACA NÃO ESTABELECE IDENTIDADE. `PRODUCT_URL` identifica o PRODUTO PAI, não o
       documento; `ORIGINAL_FILENAME` colide (`robots.txt`). As duas entram como evidência
       de contexto e nunca como prova de identidade.
    3. AUSÊNCIA DECLARADA É RESULTADO. Balde vazio é escrito com o porquê. `UNKNOWN` nunca
       é promovido a estado, e campo desconhecido é declarado, nunca omitido.

DETERMINISMO
    `RECONCILED_AT` é constante declarada, como `BACKFILL_AT` no Passaporte e
    `ES_REFERENCE_DATE` em `metricas_canonicas.py`. As fontes de prova são fixadas por
    SHA do BLOB, não por branch: branch anda, conteúdo não. Rodar duas vezes produz byte
    a byte o mesmo artefato.

    python3 scripts/it_supabase_reconciliar.py            # escreve os artefatos
    python3 scripts/it_supabase_reconciliar.py --conferir # só confere e devolve código
"""

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-SUPABASE-COLETA')

RECONCILED_AT = '2026-09-05'
RULE_VERSION = 'IT-RECONCILE-1.0'
PASSPORT_RULE_VERSION = 'PASSPORT-1.0'          # o vocabulário que a sombra imita
COLLECTION_ID = 'IT-ADAMA-CATALOG-2026-08-30'
SOURCE_ID = 'IT-ADAMA-CATALOG'
BUCKET = 'raw'
PREFIXO = 'IT/adama-website'
RAW_EXPECTED = 195


class Recusado(Exception):
    pass


# ── 1 · FONTES DE PROVA ────────────────────────────────────────────────────────────
#
# Cada fonte é fixada pelo SHA do BLOB. Um blob é imutável: se o conteúdo mudar, o SHA
# muda e este script para em vez de reconciliar contra outra coisa com o mesmo nome.
# `RAMO` é informativo — serve para a pessoa achar o arquivo, nunca para resolver o
# conteúdo.

FONTES = (
    {'NOME': 'PRESERVACAO_RELATORIO',
     'BLOB': 'b83f78c4619a91f1ac1d57b3383ea550e39afe5f',
     'RAMO': 'claude/adama-it-local-catalog',
     'CAMINHO': 'data/samples/IT-CATALOGO/IT-ADAMA-PRESERVACAO-RELATORIO.json',
     'PAPEL': 'INVENTARIO_BASE · prova de preservação com SHA256 conferido depois do download de volta'},
    {'NOME': 'PRESERVACAO_PLANO',
     'BLOB': '30d8c170010333d063a7bfa08323af22352dcae9',
     'RAMO': 'claude/adama-it-local-catalog',
     'CAMINHO': 'data/samples/IT-CATALOGO/IT-ADAMA-PRESERVACAO-PLANO.json',
     'PAPEL': 'INVENTARIO_ESPELHO · a lista do que precisava subir, com o hash lido do disco'},
    {'NOME': 'CATALOGO_CENSO',
     'BLOB': '1d451a194c0a7124a3e6540d99665ed1bc0cf0dc',
     'RAMO': 'claude/adama-it-local-catalog',
     'CAMINHO': 'data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-CENSUS.json',
     'PAPEL': 'CENSO · conta o material do catálogo'},
    {'NOME': 'CATALOGO_MEDIDO',
     'BLOB': 'aa35fdf47d08cd22a883e214eb441fc8b73cc18a',
     'RAMO': 'claude/adama-it-local-catalog',
     'CAMINHO': 'data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-MEASURED.json',
     'PAPEL': 'CENSO · o lado medido do catálogo'},
    {'NOME': 'CENSO_02_09',
     'BLOB': '9d5d18b4b09f6adb6a0240199bbcc187bbb19261',
     'RAMO': 'claude/adama-italia-product-intelligence-deep',
     'CAMINHO': 'data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-CENSUS-2026-09-02.json',
     'PAPEL': 'CENSO · segunda passagem, 2026-09-02'},
    {'NOME': 'LABEL_MANIFEST',
     'BLOB': '7825a1a69bca9a6c7f2a6dcbfc7dd85f0e804b15',
     'RAMO': 'claude/adama-italia-product-intelligence-deep',
     'CAMINHO': 'research/adama-italy-product-intelligence-deep/LABEL-MANIFEST.json',
     'PAPEL': 'VEREDICTO_DE_LEITURA dos documentos · DOCUMENT_STATE, PARSE_STATE, PARSE_BLOCKER'},
    {'NOME': 'PRODUTOS_COMERCIAIS',
     'BLOB': 'c8e4045469366e24faf95bad738e9d763d687494',
     'RAMO': 'claude/adama-italia-product-intelligence-deep',
     'CAMINHO': 'research/adama-italy-product-intelligence-deep/PRODUCTS-COMMERCIAL.json',
     'PAPEL': 'FATO_DERIVADO das páginas de produto · princípio ativo, formulação, embalagem, crosswalk'},
    {'NOME': 'ROTULOS_LEITURA',
     'BLOB': 'd4ecbe26cc456e132e587e99b24e5cc8176e92ca',
     'RAMO': 'claude/retomada-coleta-video-convegni-vz50er',
     'CAMINHO': 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json',
     'PAPEL': 'VEREDICTO_DE_LEITURA da rota Ministero · READ_STATUS e TEXT_CHARS por rótulo'},
    {'NOME': 'ROTULOS_COBERTURA',
     'BLOB': '1d8cf08b1ed8a2ff4dfc574fbd50a28262bf663d',
     'RAMO': 'claude/retomada-coleta-video-convegni-vz50er',
     'CAMINHO': 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-COBERTURA-V1.json',
     'PAPEL': 'COBERTURA da rota Ministero · onde o texto lido foi persistido'},
    {'NOME': 'ROTULOS_MANIFESTO',
     'BLOB': '2ab06a043ee708416269a55094f0ddacb441281f',
     'RAMO': 'claude/adama-italia-product-intelligence-deep',
     'CAMINHO': 'data/raw/IT-ROTULOS/_MANIFESTO.json',
     'PAPEL': 'INVENTARIO de outra coleta (163 rótulos do Ministero) · usado só para cruzar hash'},
)

FONTES_POR_NOME = {f['NOME']: f for f in FONTES}


def _blob(sha):
    """Lê um blob do objeto store. Confere o SHA de volta: pin que não é conferido é fé."""
    try:
        bruto = subprocess.run(['git', 'cat-file', 'blob', sha],
                               cwd=ROOT, check=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        raise Recusado(
            'blob %s ausente. Rode `git fetch --all` — as provas vivem em branches de '
            'trabalho, e sem elas esta reconciliação não pode ser derivada.' % sha)
    cabeca = b'blob %d\0' % len(bruto)
    lido = hashlib.sha1(cabeca + bruto).hexdigest()
    if lido != sha:
        raise Recusado('blob %s devolveu conteúdo com SHA %s' % (sha, lido))
    return bruto


def carregar(nome):
    return json.loads(_blob(FONTES_POR_NOME[nome]['BLOB']).decode('utf-8'))


def prova(nome, detalhe):
    """Uma citação de prova.

    Só o NOME da fonte entra na linha do item. Caminho, ramo e SHA do blob vivem uma vez em
    FONTES_DE_PROVA, no cabeçalho do artefato — repeti-los em cada uma das ~800 citações
    engordaria o pack sem acrescentar um fato, e a casa já mediu que gzip não perdoa isso.
    """
    if nome not in FONTES_POR_NOME:
        raise Recusado('citação a fonte não declarada: %s' % nome)
    return {'FONTE': nome, 'DETALHE': detalhe}


# ── 2 · IDENTIDADE ─────────────────────────────────────────────────────────────────
#
# A chave natural do objeto é o endereço dele no balde. Não é o caminho local (que é da
# máquina que capturou) e não é a URL (que é da origem, e uma origem pode servir dois
# objetos e dois objetos podem ter a mesma origem).

CHAVES_FORTES = ('SHA256', 'OBJETO', 'ARQUIVO_LOCAL', 'SOURCE_URL')
CHAVES_FRACAS = ('PRODUCT_URL', 'ORIGINAL_FILENAME')


def identity_basis(item):
    return 'SUPABASE:%s:%s' % (BUCKET, item['OBJETO'])


def item_id(basis):
    return 'ITEM-' + hashlib.sha1(basis.encode('utf-8')).hexdigest()[:16].upper()


# ── 3 · CROSSWALK ──────────────────────────────────────────────────────────────────

def reconciliar():
    relatorio = carregar('PRESERVACAO_RELATORIO')
    itens = relatorio['ITENS']
    if len(itens) != RAW_EXPECTED:
        raise Recusado('inventário com %d itens; o lote declarado é %d' % (len(itens), RAW_EXPECTED))

    plano = carregar('PRESERVACAO_PLANO')
    censo_doc = carregar('CATALOGO_CENSO')
    censo = json.dumps(censo_doc, ensure_ascii=False)
    medido = json.dumps(carregar('CATALOGO_MEDIDO'), ensure_ascii=False)
    censo02 = json.dumps(carregar('CENSO_02_09'), ensure_ascii=False)

    # O censo do catálogo não só CONTA o documento: ele carrega campos que só existem
    # se alguém abriu o PDF. `adama_it_catalogo.py::tipar_documento` chama
    # `pdf_text.text()` no arquivo local e casa frases que o próprio documento carrega
    # ("scheda di dati di sicurezza", "etichetta autorizzata"). Isso é uma VARREDURA
    # LÉXICA — e é a diferença entre "não foi lido" e "um classificador tocou o texto".
    censo_por_sha = {}
    for d in censo_doc.get('DOCUMENTS', []):
        censo_por_sha.setdefault(d.get('SHA256'), []).append(d)

    docs = carregar('LABEL_MANIFEST')['DOCUMENTS']
    doc_por_sha = {}
    for d in docs:
        doc_por_sha.setdefault(d['SHA256'], []).append(d)

    produtos = carregar('PRODUTOS_COMERCIAIS')['PRODUCTS']
    prod_por_sha = {p['SHA256']: p for p in produtos if p.get('SHA256')}

    rotulos = carregar('ROTULOS_LEITURA')['ITEMS']
    rot_por_sha = {r['SHA256']: r for r in rotulos if r.get('SHA256')}
    cobertura = {c['HASH_SHA256']: c for c in carregar('ROTULOS_COBERTURA')['ITEMS']}

    # A quase-cobertura que engana. 118 documentos da ADAMA carregam o MESMO NÚMERO DE
    # REGISTRO de um rótulo do Ministero que a casa leu — e não são o mesmo arquivo: são
    # outra renderização do mesmo rótulo autorizado, com bytes diferentes. Ler o rótulo do
    # Ministero do GOLTIX não é ter lido o PDF que a ADAMA hospeda em media/NNNN.
    #
    #     HASH DIFERENTE = OBJETO DIFERENTE = NÃO FOI LIDO
    #
    # Isso entra como EVIDÊNCIA DE CONTEXTO — nunca como identidade — porque é exatamente
    # o tipo de vizinhança que, daqui a seis meses, alguém confundiria com cobertura.
    rot_por_registro = {}
    for r in rotulos:
        chave = str(r.get('REGISTRATION_ID') or '').lstrip('0')
        if chave:
            rot_por_registro.setdefault(chave, r)

    # conteúdo repetido: dois objetos distintos com os mesmos bytes. Não é erro — é fato,
    # e a PROVENANCE de cada um continua inteira. Fica registrado para não virar surpresa.
    por_conteudo = {}
    for x in itens:
        por_conteudo.setdefault(x['SHA256'], []).append(x['OBJETO'])
    conteudo_repetido = {s: o for s, o in por_conteudo.items() if len(o) > 1}

    saida = []
    for x in itens:
        r = {
            'ITEM_ID': item_id(identity_basis(x)),
            'IDENTITY_BASIS': identity_basis(x),
            'OBJETO': x['OBJETO'],
            'ESPECIE': x['ESPECIE'],
            'ARQUIVO_LOCAL': x['ARQUIVO_LOCAL'],
            'ORIGINAL_FILENAME': x['ORIGINAL_FILENAME'],
            'SHA256': x['SHA256'],
            'BYTES': x['BYTES'],
            'MEDIA_TYPE': x['MEDIA_TYPE'],
            'SOURCE_URL': x.get('SOURCE_URL'),
            'PRODUCT_URL': x.get('PRODUCT_URL'),
            'PROVENANCE_COUNT': x.get('PROVENANCE_COUNT', 0),
            'PRESERVATION_STATE': x['ESTADO'],
            'PRESERVED': bool(x.get('PRESERVADO')),
            'BYTES_VERIFIED_REMOTELY': x.get('BYTES_DE_VOLTA'),
            'SHA256_REMOTO': x.get('SHA256_REMOTO'),
            'CONTENT_SHARED_WITH': [o for o in conteudo_repetido.get(x['SHA256'], []) if o != x['OBJETO']],
            'EVIDENCIA': [],
            'EVIDENCIA_DE_CONTEXTO': [],
            'VARREDURA_LEXICA': None,
        }

        ev = r['EVIDENCIA']
        ev.append(prova('PRESERVACAO_RELATORIO',
                        'ESTADO=%s · SHA256 conferido depois do download de volta · BYTES=%s'
                        % (x['ESTADO'], x.get('BYTES_DE_VOLTA'))))
        ev.append(prova('PRESERVACAO_PLANO', 'objeto listado no plano de preservação'))

        # censos: contam o objeto como material do catálogo (chave forte).
        for nome, texto in (('CATALOGO_CENSO', censo), ('CATALOGO_MEDIDO', medido),
                            ('CENSO_02_09', censo02)):
            if x['SHA256'] in texto or x['ARQUIVO_LOCAL'] in texto:
                ev.append(prova(nome, 'objeto contado no censo por chave forte'))

        # ── leitura e fato derivado ────────────────────────────────────────────────
        leitura = 'NOT_READ'
        fato = None
        recusa = None

        if x['ESPECIE'] == 'PRODUCT_DOM' and x['SHA256'] in prod_por_sha:
            p = prod_por_sha[x['SHA256']]
            campos = [c for c in ('ACTIVE_INGREDIENT', 'FORMULATION', 'PACKAGE_SIZE',
                                  'CATEGORY_DISPLAY', 'REGISTRATION_ANCHOR_TEXT') if p.get(c)]
            if campos:
                leitura = 'READ'
                fato = {
                    'ONDE': 'PRODUTOS_COMERCIAIS',
                    'PRODUTO': p.get('PRODUCT_NAME'),
                    'CAMPOS_DERIVADOS': campos,
                    'DOCUMENT_LINKS_ON_PAGE': p.get('DOCUMENT_LINKS_ON_PAGE'),
                    'CROSSWALK_STATE': (p.get('CROSSWALK') or {}).get('STATE'),
                    'ALL_DOCUMENTS_ROUTE_STATE': p.get('ALL_DOCUMENTS_ROUTE_STATE'),
                }
                ev.append(prova('PRODUTOS_COMERCIAIS',
                                'HTML lido e virou fato: %s · produto %s'
                                % (', '.join(campos), p.get('PRODUCT_NAME'))))

        if x['ESPECIE'] == 'DOCUMENT':
            # Primeiro a varredura léxica, medida na máquina que TINHA os bytes.
            cs = censo_por_sha.get(x['SHA256'], [])
            sinais = [c for c in cs if c.get('TYPE_FROM_CONTENT')
                      or c.get('PRODUCTS_NAMED_IN_DOCUMENT')
                      or c.get('CONTENT_READABLE') is not None]
            if sinais:
                c0 = sinais[0]
                leitura = 'LEXICALLY_SCANNED'
                varredura = {
                    'ONDE': 'CATALOGO_CENSO',
                    'QUEM': 'scripts/adama_it_catalogo.py :: tipar_documento → scripts/pdf_text.py',
                    'TYPE_DECIDED_BY': c0.get('TYPE_DECIDED_BY'),
                    'TYPE_FROM_CONTENT': c0.get('TYPE_FROM_CONTENT'),
                    'PRODUCTS_NAMED_IN_DOCUMENT': c0.get('PRODUCTS_NAMED_IN_DOCUMENT') or [],
                    'CONTENT_READABLE': c0.get('CONTENT_READABLE'),
                    'TYPE_SIGNALS_DISAGREE': c0.get('TYPE_SIGNALS_DISAGREE'),
                    'COVERS_MULTIPLE_PRODUCTS': c0.get('COVERS_MULTIPLE_PRODUCTS'),
                    'O_QUE_ELA_NAO_E': 'varredura léxica NUNCA satisfaz INTELLIGENCE_READING. '
                                       'Um classificador tocou o texto; ninguém leu o documento.',
                }
                r['VARREDURA_LEXICA'] = varredura
                ev.append(prova('CATALOGO_CENSO',
                                'PDF aberto por pdf_text.py na máquina que tinha os bytes: '
                                'TYPE_DECIDED_BY=%s · TYPE_FROM_CONTENT=%s · CONTENT_READABLE=%s'
                                % (c0.get('TYPE_DECIDED_BY'), c0.get('TYPE_FROM_CONTENT'),
                                   c0.get('CONTENT_READABLE'))))

            ds = doc_por_sha.get(x['SHA256'], [])
            if ds:
                d = ds[0]
                ev.append(prova('LABEL_MANIFEST',
                                'DOCUMENT_STATE=%s · PARSE_STATE=%s · CONTENT_READABLE=%s'
                                % (d.get('DOCUMENT_STATE'), d.get('PARSE_STATE'),
                                   d.get('CONTENT_READABLE'))))
                if d.get('PARSE_STATE') == 'NOT_PARSED':
                    recusa = {
                        'DECLARADA_EM': 'LABEL_MANIFEST',
                        'NAO_CONTRADIZ_A_VARREDURA':
                            'a varredura léxica aconteceu em 2026-08-30, na máquina que tinha '
                            'os bytes; o NOT_PARSED é de 2026-09-02, num ambiente onde o PDF '
                            'não era alcançável. São dois ambientes, não duas versões do fato.',
                        'PARSE_STATE': d.get('PARSE_STATE'),
                        'PARSE_BLOCKER': d.get('PARSE_BLOCKER'),
                        'LABEL_DATE_STATE': d.get('LABEL_DATE_STATE'),
                        'CONTENT_READABLE': d.get('CONTENT_READABLE'),
                        'SERVE_PRODUTOS': sorted({e.get('PRODUCT_NAME') for e in ds if e.get('PRODUCT_NAME')}),
                        'DOCUMENT_TYPE': d.get('DOCUMENT_TYPE'),
                    }

            if ds and x['SHA256'] not in rot_por_sha:
                registros = {str(d.get('REGISTRATION_NUMBER') or '').lstrip('0') for d in ds}
                vizinhos = sorted(registros & set(rot_por_registro))
                if vizinhos:
                    r['EVIDENCIA_DE_CONTEXTO'].append({
                        'TIPO': 'MESMO_REGISTRO_OUTRO_ARQUIVO',
                        'REGISTROS': vizinhos,
                        'ROTULO_LIDO_DO_MINISTERO': [rot_por_registro[v]['PRODUCT'] for v in vizinhos],
                        'POR_QUE_NAO_CONTA_COMO_LEITURA':
                            'hash diferente é objeto diferente. É outra renderização do mesmo '
                            'rótulo autorizado — dívida de leitura, nunca crédito.',
                        'CHAVE': 'FRACA · REGISTRATION_ID',
                    })

            # a rota cruzada: o mesmo PDF que a casa baixou do Ministero e LEU.
            if x['SHA256'] in rot_por_sha:
                rr = rot_por_sha[x['SHA256']]
                cc = cobertura.get(x['SHA256'], {})
                if rr.get('READ_STATUS') == 'READ':
                    leitura = 'READ'
                    fato = {
                        'ONDE': 'ROTULOS_LEITURA',
                        'ROTA': 'MINISTERO_ETICHETTASERVLET',
                        'REGISTRATION_ID': rr.get('REGISTRATION_ID'),
                        'PRODUTO': rr.get('PRODUCT'),
                        'TEXT_CHARS': rr.get('TEXT_CHARS'),
                        'TEXTO_PERSISTIDO_EM': cc.get('TEXT_FILE'),
                        'PARSED_FIELDS': cc.get('PARSED_FIELDS'),
                        'SHA_MATCHES_HOUSE_DOWNLOAD': rr.get('SHA_MATCHES_2026_08_30'),
                    }
                    ev.append(prova('ROTULOS_LEITURA',
                                    'mesmos bytes lidos pela rota Ministero · READ · %s caracteres'
                                    % rr.get('TEXT_CHARS')))
                    ev.append(prova('ROTULOS_COBERTURA',
                                    'texto persistido em %s' % cc.get('TEXT_FILE')))

        r['CONTENT_READ_STATE'] = leitura
        r['FATO_DERIVADO'] = fato
        r['RECUSA_DECLARADA'] = recusa
        saida.append(r)

    return relatorio, plano, saida, conteudo_repetido


# ── 4 · OS SEIS BALDES ─────────────────────────────────────────────────────────────
#
# Disjuntos e ORDENADOS: o primeiro que casa leva o item. Um item em dois baldes faria a
# contabilidade somar 195 sem fechar em 195, que é exatamente o defeito que este arquivo
# existe para não ter.

BALDES = (
    'ALREADY_CONSUMED',
    'KNOWN_NOT_CONSUMED',
    'ALREADY_ACCOUNTED',
    'SUPABASE_ONLY',
    'AMBIGUOUS',
    'UNKNOWN',
)

CENSOS = {'CATALOGO_CENSO', 'CATALOGO_MEDIDO', 'CENSO_02_09'}
INVENTARIO = {'PRESERVACAO_RELATORIO', 'PRESERVACAO_PLANO'}


def balde(r, bordas):
    """Devolve (BALDE, POR_QUE). `bordas` é o veredicto humano/derivado dos casos de borda."""
    fontes = {e['FONTE'] for e in r['EVIDENCIA']}
    tem_censo = bool(fontes & CENSOS)

    if r['CONTENT_READ_STATE'] == 'READ' and r['FATO_DERIVADO']:
        return 'ALREADY_CONSUMED', (
            'o conteúdo foi lido e virou fato derivado em %s — as duas provas citadas'
            % r['FATO_DERIVADO']['ONDE'])

    if r['CONTENT_READ_STATE'] == 'READ' and not r['FATO_DERIVADO']:
        return 'AMBIGUOUS', 'há selo de leitura sem fato derivado citado — leitura sem destino'

    if r['CONTENT_READ_STATE'] == 'LEXICALLY_SCANNED' and not r['RECUSA_DECLARADA']:
        return 'AMBIGUOUS', (
            'há varredura léxica e nenhuma declaração sobre a leitura — o estado intermediário '
            'existe, o veredicto sobre ele não')

    if r['RECUSA_DECLARADA']:
        if r['VARREDURA_LEXICA']:
            return 'KNOWN_NOT_CONSUMED', (
                'um classificador tocou o texto (varredura léxica medida) e ninguém leu o '
                'documento: varredura léxica NUNCA satisfaz INTELLIGENCE_READING. O motivo '
                'da não leitura está escrito: %s' % r['RECUSA_DECLARADA'].get('PARSE_BLOCKER'))
        return 'KNOWN_NOT_CONSUMED', (
            'contado no acervo e declarado NÃO LIDO com motivo: %s'
            % r['RECUSA_DECLARADA'].get('PARSE_BLOCKER'))

    borda = bordas.get(r['OBJETO'])
    if borda:
        return borda['BALDE'], borda['POR_QUE']

    if tem_censo:
        return 'ALREADY_ACCOUNTED', 'contado num censo por chave forte, sem veredicto de leitura'

    if fontes <= INVENTARIO:
        return 'SUPABASE_ONLY', (
            'fora do balde, só a prova de preservação o conhece: nenhum censo o conta e '
            'nenhum artefato deriva fato dele')

    return 'UNKNOWN', 'nenhuma evidência encontrada — e isto é um defeito do crosswalk, não um estado'


# ── 5 · A PENEIRA TÉCNICA ──────────────────────────────────────────────────────────
#
# A primeira pergunta NÃO é relevância. É "este material é tecnicamente utilizável?".
# DEFER é "não utilizável AINDA" — não é reprovação e a fila continua cobrando.
# REJECT exige julgamento declarado com evidência; a máquina nunca rejeita por ausência.

def peneira(r, balde_do_item):
    if r['PRESERVATION_STATE'] not in ('ALREADY_PRESENT_VERIFIED', 'VERIFIED'):
        return ('ERROR', 'PRESERVATION_UNVERIFIED',
                'o objeto não tem bytes conferidos no balde; reexecutar a preservação',
                'CAPTURE_ERROR')

    if balde_do_item == 'ALREADY_CONSUMED':
        return ('KEEP', 'CONSUMED_WITH_DERIVED_FACT',
                'nenhuma — o material já é fato na casa', None)

    if balde_do_item == 'KNOWN_NOT_CONSUMED':
        legivel = (r['RECUSA_DECLARADA'] or {}).get('CONTENT_READABLE')
        if legivel is False:
            return ('DEFER', 'CONTENT_DECLARED_UNREADABLE',
                    'reler o PDF a partir do balde e, se o texto não sair, declarar a rota '
                    'de texto fechada para este documento — não rejeitar por ausência',
                    'CONTENT_NOT_PROCESSED')
        if r['VARREDURA_LEXICA']:
            return ('DEFER', 'LEXICALLY_SCANNED_NOT_READ',
                    'o texto já saiu do PDF uma vez, para tipar o documento em até 3 páginas. '
                    'A próxima ação é LER o documento inteiro a partir do balde e selar '
                    'CONTENT_READ com evidência — nunca promover a varredura a leitura',
                    'CONTENT_NOT_PROCESSED')
        return ('DEFER', 'CONTENT_NOT_REACHABLE_IN_THIS_ENVIRONMENT',
                'ler o conteúdo A PARTIR DO BALDE, onde ele está com hash conferido, em vez '
                'de tentar adama.com de novo — a rota da origem devolve 403 e o Ministero '
                'serve cadeia TLS incompleta',
                'CONTENT_NOT_PROCESSED')

    if balde_do_item in ('ALREADY_ACCOUNTED', 'SUPABASE_ONLY'):
        return ('DEFER', 'ROLE_DECLARED_NO_READING_YET',
                'decidir na abertura da Inteligência se este objeto vira leitura ou fica '
                'como testemunha da captura',
                'CONTENT_NOT_PROCESSED')

    if balde_do_item == 'AMBIGUOUS':
        return ('DEFER', 'EVIDENCE_CONFLICT',
                'resolver a evidência conflitante antes de qualquer leitura', None)

    return ('ERROR', 'NO_EVIDENCE', 'refazer o crosswalk para este objeto', None)


# ── 6 · PRÉ-PASSAPORTE SOMBRA ──────────────────────────────────────────────────────
#
# SOMBRA quer dizer: usa o vocabulário fechado de PASSPORT-1.0, e NÃO É PASSAPORTE.
# Não escreve em data/passaporte/EVENTOS.jsonl, não sela evento, não passa por portão.
# É a projeção que o Passaporte TERIA se estes 195 entrassem — para que o dia da entrada
# seja uma migração declarada e não uma digitação.

ESCADA = ('CAPTURE', 'NORMALIZATION', 'DEDUP', 'CONTENT_ACQUISITION',
          'INTELLIGENCE_READING', 'CLAIM_EXTRACTION', 'ROUTING', 'CONSUMPTION')


def sombra(r, balde_do_item, triagem):
    veredicto, motivo, proxima, reason_code = triagem

    dedup = 'DUPLICATE' if r['CONTENT_SHARED_WITH'] else 'UNIQUE'
    lido = r['CONTENT_READ_STATE'] == 'READ'
    varrido = r['CONTENT_READ_STATE'] == 'LEXICALLY_SCANNED'

    # Normalizado quer dizer: o bruto tem projeção estruturada com dono. Uma linha de
    # censo com SHA, bytes, tipo e vínculo de produto É essa projeção — e ela é derivada da
    # evidência, não digitada. Quem não está em censo nenhum fica PENDING, que é a verdade
    # sobre ele, não uma lacuna de preenchimento.
    censado = bool({e['FONTE'] for e in r['EVIDENCIA']} & CENSOS)

    estados = {
        'RAW_STATE': 'PRESERVED' if r['PRESERVED'] else 'UNKNOWN',
        'NORMALIZATION_STATE': 'NORMALIZED' if censado else 'PENDING',
        # conteúdo repetido é fato preservado, não item duplicado a descartar: as duas
        # procedências continuam inteiras. O selo diz que os bytes se repetem.
        'DEDUP_STATE': dedup,
        'CONTENT_STATE': 'AVAILABLE',   # está no balde, com bytes conferidos de volta
        # LEXICALLY_SCANNED é o estado que o contrato do Passaporte existe para criar:
        # registra que um classificador tocou o texto, e NUNCA satisfaz a leitura.
        'CONTENT_READ_STATE': 'READ' if lido else ('LEXICALLY_SCANNED' if varrido else 'NOT_READ'),
        'IDENTITY_STATE': 'PROVED',     # SHA256 conferido depois do download de volta
        'CLAIM_STATE': 'EXTRACTED' if r['FATO_DERIVADO'] else 'PENDING',
        'GEOGRAPHY_STATE': 'PROVED',    # IT declarado na captura e no objeto
        'TIME_STATE': 'PROVED' if lido else 'NOT_KNOWN',
        'CROP_STATE': 'UNKNOWN',
        'ISSUE_STATE': 'UNKNOWN',
        'LINEAGE_STATE': 'ROOT',
        'INTELLIGENCE_STATE': 'PRODUCED' if r['FATO_DERIVADO'] else 'PENDING',
        'ROUTING_STATE': 'PENDING',
        # o item pode ter virado fato sem que uma capacidade o tenha consumido: consumo é
        # pergunta da Inteligência, e esta missão para na porta dela.
        'CONSUMPTION_STATE': 'PENDING',
    }

    estagio = 'CONSUMPTION'
    for nome in ESCADA:
        if nome == 'NORMALIZATION' and estados['NORMALIZATION_STATE'] != 'NORMALIZED':
            estagio = nome
            break
        if nome == 'DEDUP' and estados['DEDUP_STATE'] not in ('UNIQUE', 'DUPLICATE'):
            estagio = nome
            break
        if nome == 'CONTENT_ACQUISITION' and estados['CONTENT_STATE'] != 'AVAILABLE':
            estagio = nome
            break
        if nome == 'INTELLIGENCE_READING' and estados['CONTENT_READ_STATE'] != 'READ':
            estagio = nome
            break
        if nome == 'CLAIM_EXTRACTION' and estados['CLAIM_STATE'] != 'EXTRACTED':
            estagio = nome
            break
        if nome == 'ROUTING' and estados['ROUTING_STATE'] != 'ROUTED':
            estagio = nome
            break
        if nome == 'CONSUMPTION' and estados['CONSUMPTION_STATE'] not in ('CONSUMED',):
            estagio = nome
            break

    # Os campos constantes do lote (SHADOW, COLLECTION_ID, SOURCE_ID, SOURCE_FAMILY,
    # CAPTURED_AT, RULE_VERSION_IMITADA) vivem no cabeçalho do artefato, uma vez. Repeti-los
    # 195 vezes engordaria o pack sem acrescentar um fato — e a lei da casa é que nenhum
    # arquivo repete uma decisão que já tem dono.
    return {
        'ITEM_ID': r['ITEM_ID'],
        'IDENTITY_BASIS': r['IDENTITY_BASIS'],
        'PARENT_ITEM_ID': None,
        'DERIVED_FROM': None,
        'CONTENT_TYPE': {'PRODUCT_DOM': 'MANUFACTURER_PRODUCT_PAGE',
                         'DOCUMENT': 'MANUFACTURER_PRODUCT_DOCUMENT',
                         'CAPTURE': 'SITE_CAPTURE_ARTIFACT',
                         'MANIFEST': 'CAPTURE_MANIFEST'}[r['ESPECIE']],
        'ITEM_CLASS': 'CONTENT' if r['ESPECIE'] in ('PRODUCT_DOM', 'DOCUMENT') else 'DATASET_SNAPSHOT',
        'ESTADOS': estados,
        'CURRENT_STAGE': estagio,
        'STAGE_VERDICT': 'PASSED' if estagio == 'CONSUMPTION' else 'STOPPED_WITH_REASON',
        'NEXT_REQUIRED_STAGE': estagio,
        'TRIAGE': veredicto,
        'TRIAGE_REASON': motivo,
        'REASON_CODE': reason_code,
        'NEXT_ACTION': proxima,
        'LIFECYCLE': {'KEEP': 'ACTIVE', 'DEFER': 'DEFERRED',
                      'REJECT_WITH_REASON': 'REJECTED', 'ERROR': 'ERROR'}[veredicto],
        'BLOCKER_CODES': ([] if veredicto == 'KEEP' else [motivo]),
        'CONTENT_CHARS': (r['FATO_DERIVADO'] or {}).get('TEXT_CHARS'),
        'RECOLLECTED': 0,
        'CLAIMS': [],
        'ROUTES': [],
    }


# ── 7 · CONTROL PLANE · CANDIDATO A EVIDÊNCIA ─────────────────────────────────────
#
# Isto NÃO é estado canônico e não define o Control Plane de Coleta. É o que a casa já
# escreveu sobre esta coleta, preservado com a prova ao lado, para que o dia em que o
# Control Plane existir não comece com uma página em branco.

def control_plane(relatorio, plano):
    def c(kind, valor, fonte, detalhe, escopo, confianca):
        return {'KIND': kind, 'VALUE': valor, 'SCOPE': escopo, 'RELIABILITY': confianca,
                'EVIDENCE': prova(fonte, detalhe)}

    lm = carregar('LABEL_MANIFEST')
    gate = relatorio['GATE']
    saida = [
        c('LAST_COLLECTION_DATE', relatorio['CAPTURED_AT'], 'PRESERVACAO_RELATORIO',
          'CAPTURED_AT do lote', 'lote IT/adama-website inteiro', 'MEDIDO'),
        c('SOURCE', '%s · %s' % (relatorio['SOURCE_ID'], relatorio['source']),
          'PRESERVACAO_RELATORIO', 'campo source', 'lote inteiro', 'DECLARADO'),
        c('TEMPORAL_COVERAGE', 'catálogo público como estava em 2026-08-30; registro do '
          'Ministero em 2026-08-31 (REGISTRY_SNAPSHOT_DATE)', 'LABEL_MANIFEST',
          'REGISTRY_SNAPSHOT_DATE=%s · CATALOG_CAPTURED_AT=%s'
          % (lm.get('REGISTRY_SNAPSHOT_DATE'), lm.get('CATALOG_CAPTURED_AT')),
          'lote inteiro', 'DECLARADO'),
        c('STOP_POINT', 'DOCUMENT_CENSUS_COMPLETE=False · %s'
          % relatorio.get('DOCUMENT_CENSUS_INCOMPLETE_REASON'), 'PRESERVACAO_RELATORIO',
          plano.get('DOCUMENT_CENSUS_NOTE'), 'censo de documentos', 'MEDIDO'),
        c('GAP', 'o link "Tutti i documenti" leva a */ajax/, proibido pelo robots.txt, e não '
          'foi aberto — os documentos preservados são os que a página de produto mostra',
          'PRESERVACAO_PLANO', plano.get('DOCUMENT_CENSUS_NOTE'),
          'universo de documentos por produto', 'DECLARADO'),
        c('FAILURE', 'adama.com devolve 403 para a rota de mídia neste ambiente',
          'LABEL_MANIFEST', json.dumps(lm['RECOVERY']['ATTEMPTED_ROUTES'][:3], ensure_ascii=False),
          'releitura dos 139 documentos', 'MEDIDO'),
        c('FAILURE', 'balde Supabase sem credencial neste ambiente: '
          'NO_CREDENTIALS_IN_THIS_ENVIRONMENT', 'LABEL_MANIFEST',
          json.dumps([r for r in lm['RECOVERY']['ATTEMPTED_ROUTES']
                      if r.get('ROUTE') == 'SUPABASE_BUCKET'], ensure_ascii=False),
          'releitura a partir do balde', 'MEDIDO'),
        c('ATTEMPT', '%d rotas de recuperação tentadas, %d documentos recuperados'
          % (len(lm['RECOVERY']['ATTEMPTED_ROUTES']), lm['RECOVERY']['DOCUMENTS_RECOVERED']),
          'LABEL_MANIFEST', lm['RECOVERY']['SAMPLE_PROVES_ROUTE'],
          'releitura dos documentos', 'MEDIDO'),
        c('COVERAGE', 'PRODUCT_CENSUS_COMPLETE=%s · DOCUMENT_CENSUS_COMPLETE=%s'
          % (relatorio['PRODUCT_CENSUS_COMPLETE'], relatorio['DOCUMENT_CENSUS_COMPLETE']),
          'PRESERVACAO_RELATORIO', 'os dois censos do lote', 'lote inteiro', 'MEDIDO'),
        c('VOLUME', '%d objetos · %d bytes · maior ativo %d bytes · limite do balde %d bytes'
          % (plano['RAW_EXPECTED'], plano['BYTES_TOTAIS'], plano['LARGEST_ASSET_BYTES'],
             plano['LIMITE_BYTES']), 'PRESERVACAO_PLANO', 'contagem do plano',
          'lote inteiro', 'MEDIDO'),
        c('INTEGRITY', 'GATE=%s · SHA_VERIFIED=%d · HASH_MISMATCH=%d · BYTES conferidos %d de %d'
          % (gate['STATE'], gate['SHA_VERIFIED'], gate['HASH_MISMATCH'],
             gate['BYTES_VERIFIED_REMOTELY'], gate['BYTES_EXPECTED']),
          'PRESERVACAO_RELATORIO', gate['WHY'], 'lote inteiro', 'MEDIDO'),
        c('REASON_FOR_COLLECTION',
          'ITALY_LOCAL_FOUNDATION_CAPTURE=%s · ITALY_DECISION_INTELLIGENCE_COMPLETE=%s'
          % (relatorio['ITALY_LOCAL_FOUNDATION_CAPTURE'],
             relatorio['ITALY_DECISION_INTELLIGENCE_COMPLETE']),
          'PRESERVACAO_RELATORIO', 'captar a fundação e responder a pergunta de decisão são '
          'coisas diferentes — a casa declarou a primeira, não a segunda',
          'lote inteiro', 'DECLARADO'),
        c('SCOPE_DECLARATION', 'NO_EAME_IMPORT=%s · ITALY_CATALOG_HANDOFF_READY=%s'
          % (relatorio['NO_EAME_IMPORT'], relatorio['ITALY_CATALOG_HANDOFF_READY']),
          'PRESERVACAO_RELATORIO', 'declarações de escopo do lote', 'lote inteiro', 'DECLARADO'),
    ]

    # A lacuna que o crosswalk encontrou olhando para o lado. O código italiano abre uma
    # lista FECHADA de arquivos do acervo; dois deles foram preservados e três não. Os três
    # que ficaram de fora são justamente aqueles de que o censo completo depende — e eles
    # só existem no disco da máquina que coletou. Se aquela máquina se perder, o censo não
    # é re-derivável, e nenhum dos 195 avisa isso.
    saida.append(c(
        'GAP',
        'três arquivos do acervo que a casa LÊ não estão entre os 195 preservados: '
        'amostra-10.json, documentos-amostra.json, documentos-censo.json',
        'PRESERVACAO_PLANO',
        'os dois MANIFEST preservados (indice-captura.json, enumeracao.json) são '
        'exatamente os que têm consumidor nomeado; os outros três, também com consumidor, '
        'ficaram fora do balde e só existem no disco da máquina que coletou',
        'reprodutibilidade do censo completo (51 produtos / 141 links)',
        'MEDIDO'))

    colheita = os.path.join(SAIDA, 'CONTROL-PLANE-COLHEITA-AGENTES.json')
    if os.path.exists(colheita):
        with open(colheita, encoding='utf-8') as fh:
            extra = json.load(fh)
        for e in extra.get('FOUND', []):
            saida.append({'KIND': e['KIND'], 'VALUE': e['VALUE'], 'SCOPE': e['SCOPE'],
                          'RELIABILITY': e['RELIABILITY'],
                          'EVIDENCE': {'FONTE': 'COLHEITA_DE_AGENTES',
                                       'CAMINHO': e['EVIDENCE_PATH'],
                                       'RAMO': None, 'BLOB': None,
                                       'DETALHE': e.get('QUOTE')}})
    return saida


# ── 8 · BORDAS ─────────────────────────────────────────────────────────────────────
#
# Os cinco objetos que nenhum censo conta como material. O veredicto de cada um está
# escrito aqui, com o porquê, porque a máquina não deve adivinhar entre "tem papel
# declarado" e "só o balde o conhece" — e um `else` silencioso viraria política.

def bordas_declaradas(itens):
    por_arquivo = {x['ARQUIVO_LOCAL']: x['OBJETO'] for x in itens}
    regras = {
        'data/raw/IT/adama-website/indice-captura.json': (
            'ALREADY_ACCOUNTED',
            'papel declarado e consumidor nomeado: scripts/adama_it_preservar.py lê este '
            'índice para montar o inventário, e tests/test_adama_it_catalogo.py o exercita'),
        'data/raw/IT/adama-website/enumeracao.json': (
            'ALREADY_ACCOUNTED',
            'papel declarado e consumidor nomeado: scripts/adama_it_catalogo.py e '
            'scripts/adama_it_preservar.py partem desta enumeração'),
        'data/raw/IT/adama-website/captures/robots.txt': (
            'SUPABASE_ONLY',
            'a tentação era chamar isto de ALREADY_ACCOUNTED, porque a razão '
            'DOCUMENT_CENSUS_INCOMPLETE_REASON=ROBOTS_DISALLOWS_AJAX_ROUTE parece derivar '
            'dele. Não deriva: a razão é string literal em adama_it_preservar.py:262, e o '
            'único código da casa que PARSEIA robots.txt busca o arquivo AO VIVO pela rede, '
            'nunca a cópia preservada. `captures` aparece uma vez em todo o código italiano '
            '— a tupla que só lista o diretório e calcula o hash. Espécie vem do nome da '
            'pasta, e classificador não é consumo'),
        'data/raw/IT/adama-website/captures/sitemap-italia-it.xml': (
            'SUPABASE_ONLY',
            'nenhum censo o conta e nenhum artefato deriva fato dele; fora do balde só a '
            'prova de preservação o conhece'),
        'data/raw/IT/adama-website/captures/home-italia-it.html': (
            'SUPABASE_ONLY',
            'nenhum censo o conta e nenhum artefato deriva fato dele; fora do balde só a '
            'prova de preservação o conhece'),
    }
    return {por_arquivo[a]: {'BALDE': b, 'POR_QUE': p} for a, (b, p) in regras.items()
            if a in por_arquivo}


# ── 9 · MONTAGEM ───────────────────────────────────────────────────────────────────

def montar():
    relatorio, plano, linhas, conteudo_repetido = reconciliar()
    itens_brutos = relatorio['ITENS']
    bordas = bordas_declaradas(itens_brutos)

    por_balde = {b: 0 for b in BALDES}
    por_triagem = {'KEEP': 0, 'DEFER': 0, 'REJECT_WITH_REASON': 0, 'ERROR': 0}
    sombras = []

    for r in linhas:
        b, porque = balde(r, bordas)
        r['BALDE'] = b
        r['BALDE_POR_QUE'] = porque
        por_balde[b] += 1

        t = peneira(r, b)
        r['TRIAGE'] = t[0]
        r['TRIAGE_REASON'] = t[1]
        r['NEXT_ACTION'] = t[2]
        r['REASON_CODE'] = t[3]
        por_triagem[t[0]] += 1

        sombras.append(sombra(r, b, t))

    total = sum(por_balde.values())
    if total != RAW_EXPECTED:
        raise Recusado('contabilidade não fecha: %d em baldes, %d esperados' % (total, RAW_EXPECTED))
    if sum(por_triagem.values()) != RAW_EXPECTED:
        raise Recusado('peneira não fecha')

    reusado = sum(1 for r in linhas if len(r['EVIDENCIA']) > len(INVENTARIO))
    lidos = sum(1 for r in linhas if r['CONTENT_READ_STATE'] == 'READ')

    contabilidade = {
        'TOTAL': RAW_EXPECTED,
        'TOTAL_ACCOUNTED': total,
        'POR_BALDE': por_balde,
        'ACCOUNTED_ANYWHERE': sum(1 for r in linhas if r['EVIDENCIA']),
        'POR_TRIAGEM': por_triagem,
        'REUSED_EXISTING_WORK': reusado,
        'ACTUALLY_READ_NOW': 0,
        'AVOIDED_READING': RAW_EXPECTED,
        'ALREADY_READ': lidos,
        'OBJECT_BYTES_AVAILABLE_IN_THIS_ENVIRONMENT': 0,
        'POR_QUE_ZERO_LEITURA_NOVA':
            'nenhum byte dos 195 existe neste ambiente: data/raw está fora do Git por '
            'política (D-003) e não há credencial do Supabase aqui. Toda leitura registrada '
            'nesta reconciliação é leitura de PROVA, nunca de objeto.',
        'QUASE_COBERTURA': {
            'OBJETOS_COM_MESMO_REGISTRO_DE_UM_ROTULO_LIDO':
                sum(1 for r in linhas
                    if any(e['TIPO'] == 'MESMO_REGISTRO_OUTRO_ARQUIVO'
                           for e in r['EVIDENCIA_DE_CONTEXTO'])),
            'POR_QUE_ISTO_ESTA_CONTADO':
                'porque é a confusão mais fácil deste lote: mesmo registro não é mesmo '
                'arquivo, e quem somasse os dois declararia uma cobertura que não existe',
        },
        'CONTEUDO_REPETIDO': {'OBJETOS': sum(len(v) for v in conteudo_repetido.values()),
                              'CONTEUDOS': len(conteudo_repetido),
                              'PARES': conteudo_repetido,
                              'POR_QUE_NAO_E_ERRO': plano['PORQUE_CONTEUDO_REPETIDO_NAO_E_ERRO']},
    }

    return relatorio, plano, linhas, sombras, contabilidade


CABECALHO = {
    'SOURCE_ID': SOURCE_ID,
    'SOURCE_COUNTRY': 'IT',
    'FACT_COUNTRY': 'IT',
    'COLLECTION_ID': COLLECTION_ID,
    'RULE_VERSION': RULE_VERSION,
    'RECONCILED_AT': RECONCILED_AT,
    'CAPTURED_AT': '2026-08-30',
    'SUPABASE_CHANGED': False,
    'CANONICAL_CHANGED': False,
    'INTELLIGENCE_CHANGED': False,
    'PORTAL_CHANGED': False,
}


def escrever(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    with open(caminho, 'w', encoding='utf-8') as fh:
        json.dump(corpo, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write('\n')
    return caminho


def main():
    conferir = '--conferir' in sys.argv
    relatorio, plano, linhas, sombras, contabilidade = montar()
    evidencia = control_plane(relatorio, plano)

    inventario = dict(CABECALHO)
    inventario.update({
        'DATASET': 'IT-195-INVENTARIO',
        'EVIDENCE_CLASS': 'DETERMINISTIC_INVENTORY',
        'O_QUE_ISTO_NAO_E': 'não é o balde. É o inventário derivado da prova de preservação, '
                            'que foi conferida com SHA256 depois de baixar cada objeto de volta.',
        'BUCKET': BUCKET, 'PREFIXO': PREFIXO,
        'FONTES_DE_PROVA': list(FONTES),
        'TOTAL': len(linhas),
        'POR_ESPECIE': {e: sum(1 for r in linhas if r['ESPECIE'] == e)
                        for e in ('PRODUCT_DOM', 'DOCUMENT', 'CAPTURE', 'MANIFEST')},
        'ITENS': [{k: r[k] for k in ('ITEM_ID', 'OBJETO', 'ESPECIE', 'ARQUIVO_LOCAL',
                                     'ORIGINAL_FILENAME', 'SHA256', 'BYTES', 'MEDIA_TYPE',
                                     'SOURCE_URL', 'PRODUCT_URL', 'PROVENANCE_COUNT',
                                     'PRESERVATION_STATE', 'BYTES_VERIFIED_REMOTELY',
                                     'CONTENT_SHARED_WITH')} for r in linhas],
    })

    crosswalk = dict(CABECALHO)
    crosswalk.update({
        'DATASET': 'IT-195-CROSSWALK',
        'EVIDENCE_CLASS': 'RECONCILIATION',
        'O_QUE_ISTO_NAO_E': 'não é julgamento de relevância e não é inteligência. É onde cada '
                            'objeto já está no acervo, e o que a casa já disse sobre ele.',
        'AS_TRES_LEIS': [
            'mencionado não é consumido: CONSUMED exige leitura E fato derivado, os dois citados',
            'chave fraca não estabelece identidade: PRODUCT_URL e ORIGINAL_FILENAME entram como contexto',
            'ausência declarada é resultado; UNKNOWN nunca é promovido a estado',
        ],
        'FONTES_DE_PROVA': list(FONTES),
        'COMO_LER_UMA_CITACAO': 'cada EVIDENCIA traz FONTE + DETALHE; o caminho, o ramo e o '
                                'SHA do blob daquela fonte estão em FONTES_DE_PROVA, acima',
        'CHAVES_FORTES': list(CHAVES_FORTES),
        'CHAVES_FRACAS': list(CHAVES_FRACAS),
        'BALDES_SAO_DISJUNTOS_E_ORDENADOS': list(BALDES),
        'JUNTA_SE_AO_INVENTARIO_POR': 'ITEM_ID — os campos do objeto (SHA256, bytes, URLs, '
                                      'estado de preservação) têm dono em IT-195-INVENTARIO.json '
                                      'e não são repetidos aqui',
        'CONTABILIDADE': contabilidade,
        'ITENS': [{k: v for k, v in r.items()
                   if k not in ('ARQUIVO_LOCAL', 'ORIGINAL_FILENAME', 'SHA256', 'BYTES',
                                'MEDIA_TYPE', 'SOURCE_URL', 'PRODUCT_URL', 'PROVENANCE_COUNT',
                                'PRESERVATION_STATE', 'PRESERVED', 'BYTES_VERIFIED_REMOTELY',
                                'SHA256_REMOTO', 'IDENTITY_BASIS')}
                  for r in linhas],
    })

    sombra_doc = dict(CABECALHO)
    sombra_doc.update({
        'DATASET': 'IT-195-PRE-PASSAPORTE-SOMBRA',
        'EVIDENCE_CLASS': 'PRE_PASSPORT_SHADOW',
        'PASSPORT_ACTIVATED': False,
        'O_QUE_ISTO_NAO_E': 'não é passaporte. Nenhum evento foi selado, nenhum portão foi '
                            'atravessado e data/passaporte/EVENTOS.jsonl não foi tocado. É a '
                            'projeção que o Passaporte teria se estes 195 entrassem — para que '
                            'a entrada seja uma migração declarada, e não uma digitação.',
        'RULE_VERSION_IMITADA': PASSPORT_RULE_VERSION,
        'VOCABULARIO': 'PASSPORT-1.0, fechado. Um valor fora dele deve ser recusado na selagem.',
        'CONSTANTES_DO_LOTE': {
            'SHADOW': True,
            'COLLECTION_ID': COLLECTION_ID,
            'SOURCE_ID': SOURCE_ID,
            'SOURCE_FAMILY': 'MANUFACTURER_PUBLIC_CATALOG',
            'SOURCE_FAMILY_NOTE': 'família fora do vocabulário fechado de PASSPORT-1.0 — '
                                  'declarada aqui como candidata',
            'CAPTURED_AT': '2026-08-30',
            'SUPABASE_OBJECT_PREFIX': '%s/%s' % (BUCKET, PREFIXO),
            'SOURCE_REFERENCE': 'tem dono em IT-195-INVENTARIO.json (SOURCE_URL, ARQUIVO_LOCAL)',
        },
        'DECISOES_QUE_A_ENTRADA_TERA_DE_TOMAR': [
            'SOURCE_FAMILY: MANUFACTURER_PUBLIC_CATALOG não existe no vocabulário fechado de '
            'PASSPORT-1.0 — ou a família entra, ou o lote é dobrado numa família existente',
            'granularidade: 195 passaportes por objeto, ou um DATASET_SNAPSHOT com UNIT_COUNT=195',
            'CONSUMPTION_STATE dos 51 já consumidos: quem foi a capacidade consumidora, e por '
            'qual caso publicado — sem isso o selo seria digitado, não derivado',
        ],
        'TOTAL': len(sombras),
        'ITENS': sombras,
    })

    pacote = dict(CABECALHO)
    keep = [r for r in linhas if r['TRIAGE'] == 'KEEP']
    defer = [r for r in linhas if r['TRIAGE'] == 'DEFER']
    pacote.update({
        'DATASET': 'IT-195-COLLECTION-PACKAGE',
        'EVIDENCE_CLASS': 'COLLECTION_PACKAGE_CANDIDATE',
        'STATE': 'READY',
        'PARA_ONDE_ELE_NAO_VAI': 'a Inteligência. Este pacote para na porta dela: não classifica '
                                 'relevância, não roteia para capacidade, não abre o Casco e não '
                                 'define a política do D1.',
        'BUCKET': BUCKET, 'PREFIXO': PREFIXO,
        'COLLECTION_ID': COLLECTION_ID,
        'UNIT_COUNT': len(linhas),
        'BYTES': plano['BYTES_TOTAIS'],
        'INTEGRITY': relatorio['GATE']['STATE'],
        'CONTABILIDADE': contabilidade,
        'KEEP': [r['OBJETO'] for r in keep],
        'DEFER': [{'OBJETO': r['OBJETO'], 'MOTIVO': r['TRIAGE_REASON'],
                   'NEXT_ACTION': r['NEXT_ACTION']} for r in defer],
        'REJECT_WITH_REASON': [],
        'POR_QUE_REJECT_ESTA_VAZIO':
            'nada aqui foi julgado inutilizável. Os dois objetos que compartilham bytes NÃO são '
            'duplicata a descartar: a casa já decidiu que hash igual não apaga origem, e as duas '
            'procedências continuam inteiras. A máquina nunca rejeita por ausência.',
        'ERROR': [r['OBJETO'] for r in linhas if r['TRIAGE'] == 'ERROR'],
        'O_UNICO_DESBLOQUEIO_QUE_FALTA':
            'ler os documentos A PARTIR DO BALDE. Eles estão lá com SHA256 conferido; a origem '
            '(adama.com) devolve 403 e a rota do Ministero serve cadeia TLS incompleta. O balde '
            'deixou de ser cópia de segurança e passou a ser a única rota viva até esse conteúdo.',
    })

    cp = dict(CABECALHO)
    cp.update({
        'DATASET': 'CONTROL-PLANE-EVIDENCE-CANDIDATE',
        'EVIDENCE_CLASS': 'CONTROL_PLANE_EVIDENCE_CANDIDATE',
        'CANONICAL': False,
        'O_QUE_ISTO_NAO_E': 'não é o Control Plane de Coleta, não é estado canônico e não define '
                            'schema. É o que a casa JÁ escreveu sobre esta coleta, preservado com '
                            'a prova ao lado, para que o dia em que o Control Plane existir não '
                            'comece com uma página em branco.',
        'TOTAL': len(evidencia),
        'POR_KIND': {k: sum(1 for e in evidencia if e['KIND'] == k)
                     for k in sorted({e['KIND'] for e in evidencia})},
        'CANDIDATOS': evidencia,
    })

    if conferir:
        print('CONTABILIDADE_FECHADA = %s' % (contabilidade['TOTAL_ACCOUNTED'] == RAW_EXPECTED))
        print(json.dumps(contabilidade, ensure_ascii=False, indent=2))
        return 0

    for nome, corpo in (('IT-195-INVENTARIO.json', inventario),
                        ('IT-195-CROSSWALK.json', crosswalk),
                        ('IT-195-PRE-PASSAPORTE-SOMBRA.json', sombra_doc),
                        ('IT-195-COLLECTION-PACKAGE.json', pacote),
                        ('CONTROL-PLANE-EVIDENCE-CANDIDATE.json', cp)):
        print('escrito: %s' % escrever(nome, corpo))

    print('')
    print('TOTAL              = %d' % contabilidade['TOTAL'])
    print('TOTAL_ACCOUNTED    = %d' % contabilidade['TOTAL_ACCOUNTED'])
    for b in BALDES:
        print('  %-20s %d' % (b, contabilidade['POR_BALDE'][b]))
    for t in ('KEEP', 'DEFER', 'REJECT_WITH_REASON', 'ERROR'):
        print('  %-20s %d' % (t, contabilidade['POR_TRIAGEM'][t]))
    print('ACTUALLY_READ_NOW  = %d' % contabilidade['ACTUALLY_READ_NOW'])
    print('AVOIDED_READING    = %d' % contabilidade['AVOIDED_READING'])
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Recusado as e:
        print('RECUSADO: %s' % e, file=sys.stderr)
        sys.exit(2)
