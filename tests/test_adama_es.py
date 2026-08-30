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
    # A familia de URL da fixture MUDOU porque o site mudou: em 2026-08-30 o catalogo
    # vivo publica em /nuestras-soluciones/<categoria>/<slug>. A intencao do teste e a
    # mesma — URL repetida nao pode inflar o denominador.
    paginas = {
        A.CATALOGO: '<html><body>'
                    '<a href="/spain/es/nuestras-soluciones/control-de-plagas/alpha">ALPHA</a>'
                    '<a href="/spain/es/nuestras-soluciones/control-de-plagas/beta">BETA</a>'
                    '<a href="/spain/es/nuestras-soluciones/control-de-plagas/alpha">ALPHA 2</a>'
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
                    '<a href="/spain/es/nuestras-soluciones/control-de-plagas/gamma">GAMMA</a>'
                    '<a href="/spain/es/about-us">Quiénes somos</a>'
                    '<a href="/spain/es/contact">Contacto</a>'
                    '<a href="/spain/es/nuestras-soluciones/x/y.pdf">Etiqueta</a>'
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

    # Este teste checava "o numero 41 nao aparece", porque 96-55=41. Em 2026-08-30 ele
    # disparou contra um numero LEGITIMO: com o registro finalmente sendo lido da ficha,
    # MATCHED_EXACT virou 41 de verdade. Testar por VALOR era o defeito — proibir um
    # numero nao prova nada sobre COMO ele nasceu.
    #
    # A prova certa e de PARTICAO: cada entrada do catalogo cai em exatamente um estado.
    # Se a soma dos estados fecha o catalogo, cada numero veio de classificar linha a
    # linha; subtracao de denominadores diferentes nao produziria isso.
    estados = ('MATCHED_EXACT', 'MATCHED_WITH_EVIDENCE', 'AMBIGUOUS', 'ADAMA_SITE_ONLY')
    soma = sum(cw.get(e, 0) for e in estados if isinstance(cw.get(e), int))
    catalogo = cw.get('PUBLIC_CATALOG_ENTRIES')
    if isinstance(catalogo, int) and catalogo:
        assert soma == catalogo, (
            'os estados do crosswalk (%d) nao fecham o catalogo (%d) — algum numero nao '
            'nasceu de classificar entrada' % (soma, catalogo))
    assert 'DIFERENCA' not in cw and 'ROPF_MENOS_CATALOGO' not in cw, (
        'apareceu campo de subtracao entre denominadores diferentes (secao 23)')


# ── 9 · o que SÓ a coleta ao vivo de 2026-08-30 revelou ─────────────────────
#
# Cada teste abaixo nasce de um defeito MEDIDO, não imaginado. O comentário diz qual.

def test_categoria_vem_da_ficha_e_nao_do_menu():
    """O menu do site lista as quatro categorias em toda página.

    Defeito medido: varrer LINKS em ordem de DOM devolvia CONTROL_DE_ENFERMEDADES para
    as 56 fichas, porque esse é o primeiro item do menu. AGIL é herbicida.
    """
    html = ('<html><body><nav>'
            '<a href="/spain/es/nuestras-soluciones?f[0]=treatment:151">Control de Enfermedades</a>'
            '<a href="/spain/es/nuestras-soluciones?f[0]=treatment:156">Control de Malas Hierbas</a>'
            '</nav><h1>AGIL</h1></body></html>')
    d = A.parsear_produto(
        html, 'https://www.adama.com/spain/es/nuestras-soluciones/control-de-malas-hierbas/agil')
    assert d['PRODUCT']['CATEGORY'] == 'CONTROL_DE_MALAS_HIERBAS', (
        'a categoria veio do menu, nao da ficha')


def test_documento_sem_extensao_na_url_ainda_e_documento():
    """A ADAMA serve por /media/<id>/download, sem extensão; o nome vive no title.

    Defeito medido: exigir extensão na URL via 0 documentos em 56 fichas — e 0 teria
    sido lido como "a ADAMA não publica rótulo", que é falso.
    """
    html = ('<html><body><h1>X</h1><a href="/spain/es/media/11/download?attachment" '
            'type="application/pdf; length=127023" title="AGIL FDS.pdf">Ficha de seguridad</a>'
            '</body></html>')
    d = A.parsear_produto(html, 'https://www.adama.com/spain/es/nuestras-soluciones/a/x')
    assert len(d['DOCUMENTS']) == 1, 'documento sem extensao na URL foi ignorado'
    doc = d['DOCUMENTS'][0]
    assert doc['FILENAME'] == 'AGIL FDS.pdf', 'nome do arquivo nao veio do title'
    assert doc['PROVA_DE_QUE_E_DOCUMENTO'], 'documento entrou sem dizer por que'


def test_dose_com_unidade_no_cabecalho_nao_vira_par():
    """CULTIVO × DOSE é dose, não par. E a unidade pode estar no cabeçalho.

    Defeito medido: a linha inteira era descartada por falta de agente, e a dose ia
    junto. O risco oposto é pior: virar par sem agente nomeado.
    """
    html = ('<html><body><h1>X</h1><h2>Registros</h2><table>'
            '<tr><th>CULTIVO</th><th>DOSIS (L/Ha)</th></tr>'
            '<tr><td>Alcachofa</td><td>3,0</td></tr></table></body></html>')
    d = A.parsear_produto(html, 'https://www.adama.com/spain/es/nuestras-soluciones/a/x')
    assert not d['CROP_ISSUE_RELATIONS'], 'linha sem agente virou par'
    doses = d['CROP_DOSE_RELATIONS']
    assert len(doses) == 1, 'a dose por cultivo se perdeu'
    assert doses[0]['DOSE'] == '3,0 l/ha', doses[0]['DOSE']
    assert doses[0]['DOSE_UNIT_SOURCE'] == 'CABECALHO_DA_TABELA'
    assert doses[0]['PAIR_DERIVABLE'] is False
    assert doses[0]['ISSUE'] == 'NÃO SEI'


def test_cabecalho_nao_atravessa_secao_diferente():
    """A herança de cabeçalho é restrita: mesma seção e mesmo número de colunas.

    Sem esse limite, o cabeçalho de uma tabela de dose contaminaria a tabela de HRAC
    da mesma ficha — e uma dose apareceria onde a ADAMA não publicou nenhuma.
    """
    tabelas = [
        {'INDICE': 0, 'SECAO': 'Registros', 'CABECALHO': ['CULTIVO', 'DOSIS (L/Ha)'],
         'LINHAS': [{'INDICE': 0, 'CELULAS': ['Ajos', '2,5']}]},
        {'INDICE': 1, 'SECAO': 'Beneficios', 'CABECALHO': [],
         'LINHAS': [{'INDICE': 0, 'CELULAS': ['Pendimetalina', 'K1']}]},
    ]
    A.herdar_cabecalho(tabelas)
    assert tabelas[1]['CABECALHO'] == [], 'cabecalho atravessou para outra secao'


def test_concentracao_em_g_por_litro_e_lida():
    """"Dicamba 120 g/l" é concentração publicada tanto quanto "10%".

    Defeito medido: COLTRANE saía com ACTIVE_INGREDIENTS vazio porque a regex só
    conhecia o símbolo de porcentagem.
    """
    ia = A._ingredientes('Composición: Dicamba 120 g/l + Mesotriona 50 g/l')
    nomes = {x['NAME'].lower(): x['CONCENTRATION'] for x in ia}
    assert 'dicamba' in nomes and nomes['dicamba'] == '120 g/l', ia


def test_captura_local_nao_apaga_falha_http():
    """Pacote do navegador não é cache: página que não veio 200 continua sendo falha."""
    A._PACOTES.clear()
    A._PACOTES[A._chave_rota('https://www.adama.com/x')] = {'status': 500, 'html': ''}
    estado, corpo, code = A.buscar('https://www.adama.com/x')
    A._PACOTES.clear()
    assert estado != 'OK' and corpo is None and code == '500', (
        'status ruim na captura virou conteudo vazio')


def test_registro_solto_so_conta_com_o_rotulo_do_lado():
    """"25186" só é registro quando a página escreve "Nº de registro:" antes.

    Defeito medido: a regex só conhecia ES-#####, e 30 das 56 fichas saíam com NÃO SEI
    tendo o numero publicado. O risco oposto — cinco digitos soltos virarem registro —
    fica fechado pela ancora no rotulo.
    """
    assert A._registro('Nº de registro: 25186 Envases: 5L') == '25186'
    assert A._registro('Nº de registro: 24.887') == '24.887'
    assert A._registro('Nº de registro: ES-01209') == 'ES-01209'
    assert A._registro('Envases: 10L. Precio 25186 pesetas') == 'NÃO SEI', (
        'numero solto sem o rotulo virou registro')


def test_cultivo_declarado_e_cultivo_citado_nao_se_somam():
    """O bloco "Cultivos" é declaração; o corpo do texto é menção. São coisas diferentes.

    Defeito medido: o filtro que limpava o titulo vazado apagava tambem cultivo real,
    porque "Trigo" tambem e titulo de outro bloco na mesma ficha. AVASTEL ficava sem
    nenhum cultivo declarado.
    """
    html = ('<html><body><h1>X</h1>'
            '<h3>Cultivos</h3><div>Cebada</div><div>Trigo</div>'
            '<h3>Trigo</h3><div>bla</div>'
            '<h3>Información Adicional del Producto</h3><div>bla</div>'
            '</body></html>')
    declarados = A.cultivos_declarados(A.estruturar(html))
    assert declarados == ['Cebada', 'Trigo'], declarados

    d = A.parsear_produto(html, 'https://www.adama.com/spain/es/nuestras-soluciones/a/x')
    fontes = {r['CROP']: r['DECLARATION_SOURCE'] for r in d['CROP_RELATIONS']}
    for crop, fonte in fontes.items():
        assert fonte in ('DECLARADO_NO_BLOCO_CULTIVOS', 'CITADO_NO_CORPO_DA_PAGINA'), crop


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
