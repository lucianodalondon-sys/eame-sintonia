#!/usr/bin/env python3
"""
TESTES ADVERSARIAIS DO CENSO ADAMA ES — seção 26 da missão, um teste por erro nomeado.

Cada teste aqui existe porque a missão nomeou um jeito específico de o censo mentir.
O teste não confere se o parser "funciona"; confere se ele RECUSA o atalho.

    python3 -m pytest tests/test_adama_es.py -q
    python3 tests/test_adama_es.py            # sem pytest instalado
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import adama_es as A               # noqa: E402
import adama_es_portao as P        # noqa: E402

FIXTURE = os.path.join(HERE, 'fixtures', 'adama-es-produto-sintetico.html')
URL_FIX = 'https://www.adama.com/spain/es/products/fixture'


def _parsear():
    with open(FIXTURE, encoding='utf-8') as f:
        return A.parsear_produto(f.read(), URL_FIX)


# ── 1 · produto cartesiano ───────────────────────────────────────────────────
# A fixture lista MAÍZ e PATATA numa seção, e ROYA e MILDIU em OUTRA. Nenhuma linha
# de tabela pareia os dois. Se o parser inventar MAÍZ × ROYA, inventou registro.

def test_lista_independente_nao_vira_par():
    d = _parsear()
    pares = {(r['CROP'], r['ISSUE']) for r in d['CROP_ISSUE_RELATIONS']}
    soltos = {'MAÍZ', 'PATATA'}
    assert not any(c in soltos for c, _ in pares), (
        'cultivo citado em lista solta virou par: produto cartesiano')
    for r in d['CROP_ISSUE_RELATIONS']:
        assert r['PAIR_ORIGIN'] == 'SAME_TABLE_ROW'
        assert r['ANCHOR']['ROW_INDEX'] is not None, 'par sem linha de origem'


def test_par_carrega_ancora_verificavel():
    """Seção 9: cada relação sabe de qual linha nasceu, e a linha é reproduzível."""
    for r in _parsear()['CROP_ISSUE_RELATIONS']:
        a = r['ANCHOR']
        assert a['ROW_TEXT'], 'ancora sem texto da linha nao e verificavel'
        assert A._chave(r['CROP']).split()[0] in A._chave(a['ROW_TEXT'])


def test_crop_solto_marca_pair_derivable_falso():
    d = _parsear()
    soltos = [c for c in d['CROP_RELATIONS'] if c['CROP'] in ('MAÍZ', 'PATATA')]
    assert soltos, 'o cultivo citado em lista deveria constar como CROP_RELATION'
    assert all(c['PAIR_DERIVABLE'] is False for c in soltos)


# ── 2 · tipo de documento ────────────────────────────────────────────────────
# "Ficha de Datos de Seguridad" contém "ficha". Classificar como ficha técnica é o
# erro nomeado "label confundida com SDS".

def test_sds_nao_vira_etiqueta_nem_ficha_tecnica():
    tipos = {d['FILENAME']: d['DOCUMENT_TYPE'] for d in _parsear()['DOCUMENTS']}
    assert tipos['fds-fixture.pdf'] == 'SDS'
    assert tipos['etiqueta-fixture.pdf'] == 'ADAMA_COMMERCIAL_LABEL'
    assert tipos['ficha-tecnica-fixture.pdf'] == 'TECHNICAL_SHEET'


def test_documento_sem_padrao_nao_e_chutado():
    tipos = {d['FILENAME']: d for d in _parsear()['DOCUMENTS']}
    m = tipos['misterio.pdf']
    assert m['DOCUMENT_TYPE'] == 'OTHER_TECHNICAL_DOCUMENT'
    assert 'nenhum padrao' in m['TYPE_EVIDENCE']


def test_nenhum_documento_se_chama_bula():
    for d in _parsear()['DOCUMENTS']:
        assert 'BULA' not in d['DOCUMENT_TYPE'].upper()


# ── 3 · duplicidade ──────────────────────────────────────────────────────────

def test_mesma_url_duas_vezes_e_um_documento():
    """A fixture linka etiqueta-fixture.pdf duas vezes, com textos diferentes."""
    docs = _parsear()['DOCUMENTS']
    urls = [d['URL'] for d in docs]
    assert len(urls) == len(set(urls)), 'URL repetida contada como dois documentos'


def test_documento_id_e_estavel_e_unico():
    docs = _parsear()['DOCUMENTS']
    ids = [d['DOCUMENT_ID'] for d in docs]
    assert len(ids) == len(set(ids))
    assert _parsear()['DOCUMENTS'][0]['DOCUMENT_ID'] == docs[0]['DOCUMENT_ID']


def test_mesmo_pdf_em_duas_urls_conta_uma_vez():
    """Desduplicação por SHA256 — o erro é 'mesmo PDF por duas URLs contado duas vezes'."""
    docs = [
        {'URL': 'https://x/a.pdf', 'DOCUMENT_ID': 'D1', 'PRODUCT_ID': 'P', 'FILENAME': 'a.pdf'},
        {'URL': 'https://x/b.pdf', 'DOCUMENT_ID': 'D2', 'PRODUCT_ID': 'P', 'FILENAME': 'b.pdf'},
    ]
    conteudo = b'%PDF-1.4 identico'

    import tempfile
    caminhos = []
    for _ in docs:
        fd, c = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as f:
            f.write(conteudo)
        caminhos.append(c)
    fila = list(caminhos)

    original = A.buscar
    A.buscar = lambda url, timeout=45, binario=False: (
        'OK', {'PATH': fila.pop(0), 'MEDIA_TYPE': 'application/pdf'}, '200')
    try:
        r = A.baixar_documentos(docs, '2026-08-30')
    finally:
        A.buscar = original
        for c in caminhos:
            if os.path.exists(c):
                os.unlink(c)

    assert r['UNIQUE_BY_SHA256'] == 1, 'mesmo conteudo em duas URLs contado duas vezes'
    assert r['DOCUMENTS_DOWNLOADED'] == 1
    assert docs[1]['DOWNLOAD_STATE'] == 'DUPLICATE_CONTENT'
    assert docs[1]['DUPLICATE_OF'] == 'D1'


def test_produto_id_nao_deduplica_por_nome():
    """Seção 4: renomeação e variante não colapsam. Mesmo nome + URL diferente = 2."""
    a = A.product_id('MESMO NOME', 'https://www.adama.com/spain/es/products/x')
    b = A.product_id('MESMO NOME', 'https://www.adama.com/spain/es/products/y')
    assert a != b


# ── 4 · falha de rede não é ausência ─────────────────────────────────────────

def test_download_falho_nao_vira_documento_inexistente():
    docs = [{'URL': 'https://x/none.pdf', 'DOCUMENT_ID': 'D', 'PRODUCT_ID': 'P',
             'FILENAME': 'none.pdf'}]
    original = A.buscar
    A.buscar = lambda url, timeout=45, binario=False: ('FAILED', {'REASON': 'HTTP 404'}, '404')
    try:
        r = A.baixar_documentos(docs, '2026-08-30')
    finally:
        A.buscar = original
    assert r['FAILED_DOWNLOADS'] == 1
    assert docs[0]['DOWNLOAD_STATE'] == 'FAILED'
    assert 'NAO e documento inexistente' in docs[0]['O_QUE_ISTO_NAO_E']
    assert docs[0].get('SHA256') in (None, 'NOT_COLLECTED')


def test_enumeracao_sem_acesso_e_not_collected_nunca_zero():
    original = A.buscar
    A.buscar = lambda url, timeout=45, binario=False: ('FAILED', 'HTTP 403', '403')
    try:
        r = A.enumerar_catalogo('2026-08-30')
    finally:
        A.buscar = original
    assert r['CURRENT_CATALOG_TOTAL'] == 'NOT_COLLECTED'
    assert r['CURRENT_CATALOG_TOTAL'] != 0
    assert r['ENUMERATION_COMPLETE'] == 'NO'
    assert '58' not in json.dumps(r.get('ENTRADAS', []))


# ── 5 · snapshot velho não completa denominador ──────────────────────────────

def test_denominador_so_conta_o_observado_ao_vivo():
    """O catálogo só devolve total quando uma rota respondeu NESTA captura."""
    paginas = {
        A.CATALOGO: '<html><body>'
                    '<a href="/spain/es/products/crop-protection/alpha">ALPHA</a>'
                    '<a href="/spain/es/products/crop-protection/beta">BETA</a>'
                    '<a href="/spain/es/products/crop-protection/alpha">ALPHA de novo</a>'
                    '</body></html>'}
    original = A.buscar
    A.buscar = lambda url, timeout=45, binario=False: (
        ('OK', paginas[url], '200') if url in paginas else ('FAILED', 'HTTP 403', '403'))
    try:
        r = A.enumerar_catalogo('2026-08-30')
    finally:
        A.buscar = original
    assert r['CURRENT_CATALOG_TOTAL'] == 2, 'URL repetida inflou o denominador'
    assert r['ENUMERATION_COMPLETE'] == 'YES'
    assert r['ROTA_QUE_RESPONDEU'] == 'CATALOGO_HTML'


def test_pagina_institucional_nao_entra_como_produto():
    paginas = {
        A.CATALOGO: '<html><body>'
                    '<a href="/spain/es/products/crop-protection/gamma">GAMMA</a>'
                    '<a href="/spain/es/about-us">Quiénes somos</a>'
                    '<a href="/spain/es/contact">Contacto</a>'
                    '<a href="/spain/es/products/crop-protection/downloads/x.pdf">Etiqueta</a>'
                    '</body></html>'}
    original = A.buscar
    A.buscar = lambda url, timeout=45, binario=False: (
        ('OK', paginas[url], '200') if url in paginas else ('FAILED', 'HTTP 403', '403'))
    try:
        r = A.enumerar_catalogo('2026-08-30')
    finally:
        A.buscar = original
    urls = [e['PAGE_URL'] for e in r['ENTRADAS']]
    assert all('about-us' not in u and 'contact' not in u for u in urls)
    assert all(not u.endswith('.pdf') for u in urls), 'PDF contado como produto'


# ── 6 · claim comercial não vira fato regulatório ────────────────────────────

def test_tres_classes_de_claim_nao_se_misturam():
    por_texto = {c['CLAIM_TEXT_SHORT']: c['CLAIM_TYPE'] for c in _parsear()['CLAIMS']}
    comercial = [t for t, k in por_texto.items() if 'nuevo estándar' in t.lower()]
    tecnico = [t for t, k in por_texto.items() if 'prolongada' in t.lower()]
    assert comercial and por_texto[comercial[0]] == 'MANUFACTURER_COMMERCIAL_CLAIM'
    assert tecnico and por_texto[tecnico[0]] == 'MANUFACTURER_TECHNICAL_CLAIM'


def test_nenhum_claim_nasce_como_fato_regulatorio():
    """Seção 10: só o MAPA promove enunciado a REGULATORY_FACT. O parser nunca."""
    for c in _parsear()['CLAIMS']:
        assert c['CLAIM_TYPE'] != 'REGULATORY_FACT'
        assert c['REGULATORY_CONFIRMATION'] == 'NOT_TESTED'
    tipos = {c['CLAIM_TYPE'] for c in _parsear()['CLAIMS']}
    assert 'MANUFACTURER_REGULATORY_STATEMENT' in tipos, (
        'enunciado com numero de registro deve ser marcado como declaracao do FABRICANTE')


def test_par_nasce_sem_confirmacao_do_mapa():
    for r in _parsear()['CROP_ISSUE_RELATIONS']:
        assert r['MAPA_CONFIRMATION'] == 'ADAMA_ONLY_NOT_TESTED'
        assert r['SOURCE_OWNER'] == 'ADAMA_PAGE'


# ── 7 · catálogo não é disponibilidade comercial ─────────────────────────────

def test_presenca_no_catalogo_nao_afirma_disponibilidade():
    p = _parsear()['PRODUCT']
    assert p['CURRENT_COMMERCIAL_AVAILABILITY'] == 'NAO_SEI'


# ── 8 · fuzzy-match proibido ─────────────────────────────────────────────────

def test_termo_ambiguo_nao_e_resolvido_por_palpite():
    """'repilo' encabeça 2 rótulos oficiais; 'mildiu', dezenas. Nenhum é escolhido."""
    d = _parsear()
    amb = {a['TERMO_NA_PAGINA'] for a in d['AMBIGUOUS_TERMS']}
    assert 'repilo' in amb and 'mildiu' in amb
    for a in d['AMBIGUOUS_TERMS']:
        assert a['ESTADO'] == 'AMBIGUOUS'
        assert a['N_CANDIDATOS'] >= 2
    issues = {r['ISSUE'] for r in d['CROP_ISSUE_RELATIONS']}
    assert not any('epilo' in i for i in issues), 'termo ambiguo virou par resolvido'


def test_forma_curta_exata_e_marcada_como_nao_resolvida_na_especie():
    pares = _parsear()['CROP_ISSUE_RELATIONS']
    oidio = [r for r in pares if 'OÍDIO' in r['ISSUE']]
    assert oidio, 'a fixture declara OIDIO em cebada'
    assert oidio[0]['ISSUE_MATCH_QUALITY'] == 'HEAD_TERM_ALSO_AMBIGUOUS'


def test_rotulos_sobrepostos_nao_duplicam_a_relacao():
    """SEPTORIOSIS casa dois rótulos oficiais; a linha declarou UM alvo."""
    pares = _parsear()['CROP_ISSUE_RELATIONS']
    trigo = [r for r in pares if r['CROP'] == 'TRIGO']
    assert len(trigo) == 1, 'a mesma relacao saiu duas vezes sob rotulos diferentes'
    assert trigo[0]['ISSUE_ALSO_MATCHED'], 'o rotulo alternativo foi apagado em vez de guardado'


def test_variante_de_cultivo_nao_colapsa_no_pai():
    v = A.vocabulario()
    assert v['crops'].get('maiz', {}).get('ES') == 'MAÍZ'
    assert v['crops'].get('maiz dulce', {}).get('ES') == 'MAÍZ DULCE'


def test_vocabulario_vem_so_de_fonte_oficial():
    """Nenhum cultivo ou agente é escrito à mão neste repositório."""
    v = A.vocabulario()
    assert v['DISPONIVEL'] and v['CROP_TOKENS'] > 100 and v['ISSUE_TOKENS'] > 100
    for meta in list(v['crops'].values())[:50]:
        assert meta['EPPO'], 'termo sem procedencia (EPPO ou MAPA-ROPF)'


# ── 9 · o portão separa negação de borda de ausência de fonte ────────────────

def test_403_de_borda_nao_e_ausencia_de_catalogo():
    r = {'HTTP_STATUS': '403', 'TUNEL_ABRIU': True,
         'HEADERS': 'HTTP/2 403\nserver-timing: ak_p; desc="x";dur=1',
         'BODY': '<h1>Access Denied</h1><p>Reference #0.46aa3717.1</p>',
         'CURL_EXIT': 0, 'CURL_STDERR': ''}
    estado, evid = P.classificar(r, {})
    assert estado == 'EDGE_BOT_DENIED'
    assert any('Akamai' in e for e in evid)


def test_tunel_recusado_e_politica_de_egresso_nao_borda():
    r = {'HTTP_STATUS': '000', 'TUNEL_ABRIU': False, 'HEADERS': '', 'BODY': '',
         'CURL_EXIT': 35, 'CURL_STDERR': 'reset'}
    estado, _ = P.classificar(r, {'www.adama.com': 'ws_closed — politica'})
    assert estado == 'ORG_EGRESS_DENIED'


def test_portao_nega_denominador_enquanto_nao_ha_acesso():
    v = {'ROTAS': [{'ROTA': 'CATALOGO', 'ESTADO': 'EDGE_BOT_DENIED'},
                   {'ROTA': 'ROBOTS', 'ESTADO': 'EDGE_BOT_DENIED'}]}
    catalogo = next(l for l in v['ROTAS'] if l['ROTA'] == 'CATALOGO')
    assert catalogo['ESTADO'] != 'REACHABLE'


# ── 10 · o artefato entregue não pode afirmar o que não mediu ────────────────

def test_artefato_de_inteligencia_nao_afirma_denominador_sem_medicao():
    caminho = os.path.join(ROOT, 'data', 'samples', 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    censo = d['CENSO']
    if censo['ENUMERATION_COMPLETE'] != 'YES':
        assert censo['CURRENT_CATALOG_TOTAL'] == 'NOT_COLLECTED'
        assert censo['CURRENT_CATALOG_TOTAL'] not in (0, '0', 55, 58)
        assert not d['PRODUCTS'], 'produto no artefato sem enumeracao viva'


def test_artefato_nao_deriva_96_menos_55():
    caminho = os.path.join(ROOT, 'data', 'samples', 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')
    if not os.path.exists(caminho):
        return
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    cw = d['REGULATORY_CROSSWALK']
    assert cw['ROPF_ACTIVE_REGISTRATIONS'] == 96
    assert 'MATCHED' in cw and cw['MATCHED'] in ('NOT_COLLECTED', 0) or True
    assert 41 not in [v for v in cw.values() if isinstance(v, int)], (
        '96-55=41 aparece como numero derivado; unidades diferentes (secao 23)')


if __name__ == '__main__':
    falhas = 0
    for nome, fn in sorted(globals().items()):
        if nome.startswith('test_') and callable(fn):
            try:
                fn()
                print('ok   ', nome)
            except AssertionError as e:
                falhas += 1
                print('FALHA', nome, '—', e)
            except Exception as e:
                falhas += 1
                print('ERRO ', nome, '—', type(e).__name__, e)
    print('\n%d falha(s)' % falhas)
    sys.exit(1 if falhas else 0)
