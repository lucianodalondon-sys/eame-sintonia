#!/usr/bin/env python3
"""
CATÁLOGO ADAMA ITALIA — o que a empresa APRESENTA, medido do DOM capturado.

O contrato está em `adama_it.py`; aqui está a **medição**. Cada número sai de um
arquivo em `data/raw/IT/adama-website/`, e cada arquivo carrega sha256, bytes e
a hora da captura. Nada aqui vem da rede: o módulo lê o acervo, e o acervo foi
trazido pelo Chrome com janela desta máquina.

    ADAMA_IT_BROWSER_ROUTE = HEADED_ONLY

`curl` devolve 403 com 143 bytes e o Chrome headless devolve 183 bytes de
"Access Denied". Só a janela gráfica abre. Isso NÃO é proteção contornada — é a
mesma página que qualquer pessoa lê, pedida pelo mesmo programa.

AS ARMADILHAS QUE ESTE ARQUIVO EXISTE PARA NÃO CAIR
-----------------------------------------------------

**1 · O zero à esquerda.** O Ministero grava `016312`; a ADAMA publica `16312`.
São o MESMO registro escrito de dois jeitos. Comparar como texto reprovaria os
oito produtos da amostra que têm número — e o resultado pareceria "o catálogo
não bate com o registro". Formato não é identidade.

    REGISTRATION_ID_FORMAT ≠ REGISTRATION_ID

**2 · O termo que é botão de busca.** "Colture" e "Problematica" na página são
links para `/search?global_search_solr=...`. São termos de navegação do site,
não frases de autorização. Um produto lista 67 culturas; nenhuma delas está
escrita como uso autorizado.

    MENU_TERM ≠ AUTHORIZED_ISSUE
    CITED_CROP ≠ AUTHORIZED_CROP

**3 · As duas listas soltas.** Cultura e alvo vivem em blocos separados. Cruzá-las
produziria o par cartesiano — para um único produto da amostra, 26 culturas ×
67 alvos = 1742 pares que ninguém autorizou.

    CO_PRESENCE ≠ AUTHORIZED_PAIR

O par só nasce quando cultura e alvo estão na MESMA LINHA de uma tabela de uso.
Na amostra medida isso nunca aconteceu: as tabelas trazem cultura × dose, e
nenhuma traz coluna de alvo.

**4 · O rótulo do link mentindo sobre o arquivo.** Um link diz "Brochure" e
entrega `260119_adama_leaftlet-banjo-web (1).pdf`. Outro diz "Scheda di
sicurezza" e entrega um PDF cujo conteúdo cobre CINCO produtos. O tipo se
decide pelo CONTEÚDO; o rótulo e o nome do arquivo ficam registrados ao lado,
e a discordância vira campo.

    LABEL ≠ DOCUMENT_TYPE
    ONE DOCUMENT ≠ ONE PRODUCT

**5 · O caminho que parece identidade.** O mesmo catálogo serve produto sob
`/prodotti/` e sob `/prodotti-adama/`. A identidade é o nó interno do site
(NODE_ID) e o canonical, nunca a pasta da URL.

    PATH ≠ IDENTITY
"""
import datetime
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import adama_it as ai       # noqa: E402
import adama_it_raw as rw   # noqa: E402

ACERVO = os.path.join(RAIZ, 'data', 'raw', 'IT', 'adama-website')
DESTINO = os.path.join(RAIZ, 'data', 'samples', 'IT-CATALOGO',
                       'IT-ADAMA-CATALOG-MEASURED.json')


def ler(nome, padrao=None):
    caminho = os.path.join(ACERVO, nome)
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding='utf-8') as fh:
        return json.load(fh)


# ──────────────────────────────────── 1 · identidade do número de registro
def id_ministero(bruto):
    """→ (id comparável, estado). O zero à esquerda é formato, não identidade.

    `16312` e `016312` são o mesmo registro. Mas `0037584/22` NÃO é um registro
    do Ministero — tem barra e sete dígitos —, e por isso sai como token
    preservado, sem virar id comparável.
    """
    s = str(bruto or '').strip()
    if not s:
        return None, 'ABSENT'
    if re.fullmatch(r'\d{3,6}', s):
        return s.lstrip('0') or '0', 'MINISTERO_LIKE'
    return None, 'PRESENT_BUT_NOT_MINISTERO_FORMAT'


def indice_registro(produtos):
    por_id, por_nome = {}, {}
    for r in produtos:
        chave, _ = id_ministero(r.get('REGISTRATION_ID'))
        if chave:
            por_id.setdefault(chave, []).append(r)
        por_nome.setdefault(_nome_chave(r.get('PRODUCT')), []).append(r)
    return por_id, por_nome


_MARCA = re.compile(r'[®™©]')


def _nome_chave(s):
    s = _MARCA.sub('', str(s or ''))
    return re.sub(r'[^A-Z0-9]+', '', s.upper())


# ────────────────────────────────────────────── 2 · crosswalk com os 163
def cruzar(produto, por_id, por_nome):
    """Um produto do catálogo contra os 163 registros. Sem fundir, sem chutar."""
    bruto = produto.get('REGISTRATION_ID_AS_WRITTEN')
    chave, estado_formato = id_ministero(bruto)

    if chave:
        candidatos = por_id.get(chave) or []
        if len(candidatos) == 1:
            r = candidatos[0]
            return {'STATE': ai.LOCAL_REGISTERED,
                    'MATCHED_BY': 'REGISTRATION_ID_NORMALIZED',
                    'CLAIM_AS_WRITTEN': bruto,
                    'REGISTRATION_ID': r['REGISTRATION_ID'],
                    'REGISTRY_PRODUCT': r['PRODUCT'],
                    'HOLDER': r.get('HOLDER'),
                    'NAME_DIVERGES_FROM_REGISTRY': (
                        _nome_chave(produto.get('PRODUCT_NAME')) != _nome_chave(r['PRODUCT'])),
                    'NORMALIZATION': 'zeros à esquerda removidos dos dois lados',
                    'WHY': ('a ADAMA publica o número e ele existe entre os 163 '
                            'registros medidos no Ministero')}
        if len(candidatos) > 1:
            return {'STATE': ai.REGISTRATION_CONFLICT,
                    'MATCHED_BY': 'REGISTRATION_ID_NORMALIZED',
                    'CLAIM_AS_WRITTEN': bruto,
                    'CANDIDATE_REGISTRATION_IDS': [c['REGISTRATION_ID'] for c in candidatos],
                    'WHY': 'o mesmo número normalizado cobre mais de um registro'}
        # Presente, bem formado, e fora da fatia medida. Isto NÃO é conflito:
        # conflito é evidência que se contradiz. Aqui a minha metade é que é
        # menor — os 163 são a fatia ADAMA de um censo nacional de 17.695
        # registros, e um produto que a ADAMA distribui pode ser registrado por
        # outra empresa. Chamar de conflito acusaria a fonte do meu recorte.
        return {'STATE': ai.LOCAL_PRESENT_NOT_PROVED,
                'MATCHED_BY': 'REGISTRATION_ID_NORMALIZED',
                'CLAIM_AS_WRITTEN': bruto,
                'REASON': 'CLAIM_OUTSIDE_MEASURED_REGISTRY',
                'WHY': ('o catálogo publica um número bem formado que não está '
                        'entre os 163 registros ADAMA medidos. Os 163 são a fatia '
                        'ADAMA de um censo nacional de 17.695 registros: o número '
                        'pode existir sob outro titular. NÃO é conflito e NÃO é '
                        'prova de ausência de registro'),
                'WHAT_WOULD_CLOSE_IT': ('consultar o número no dataset nacional '
                                        'PROD_FTS do Ministero, que não está neste '
                                        'repositório')}

    candidatos = por_nome.get(_nome_chave(produto.get('PRODUCT_NAME'))) or []
    comum = {'MATCHED_BY': 'NAME_ONLY' if candidatos else None,
             'CLAIM_AS_WRITTEN': bruto,
             'REGISTRATION_FORMAT_STATE': estado_formato}
    if len(candidatos) == 1:
        return dict(comum, STATE=ai.LOCAL_PRESENT_NOT_PROVED,
                    CANDIDATE_REGISTRATION_ID=candidatos[0]['REGISTRATION_ID'],
                    WHY=('o nome bate com um registro só, e nome não é registro. '
                         'Candidato anotado, identidade não fechada'))
    if len(candidatos) > 1:
        return dict(comum, STATE=ai.REGISTRATION_CONFLICT,
                    CANDIDATE_REGISTRATION_IDS=[c['REGISTRATION_ID'] for c in candidatos],
                    WHY='o mesmo nome comercial cobre mais de um registro')
    return dict(comum, STATE=ai.LOCAL_PRESENT_NOT_PROVED,
                WHY=('presente no catálogo e sem correspondência provada. NÃO é '
                     'NOT_REGISTERED: exigiria consulta ao Ministero que devolvesse '
                     'ausência, não a minha falta de casamento'))


# ─────────────────────────────────────────── 3 · tabelas: o par ancorado
# A ORDEM É A REGRA, e ela já custou um defeito: com CROP antes de TIMING, a
# coluna **"Quando trattare la coltura"** virava cultura — porque a palavra
# "coltura" está escrita dentro dela. A tabela ficava com duas colunas de
# cultura, a segunda era descartada, e APPLICATION_WINDOWS saía 0 tendo janela
# na fonte. Marcador de tempo é inequívoco; "coltura" dentro de uma frase, não.
PAPEL_COLUNA = (
    ('PHI', r'intervallo di sicurezza|tempo di carenza|carenza'),
    ('DOSE', r'\bdos[ei]\b|dosaggi'),
    ('ISSUE', r'avversit|infestant|patogen|malatti|parassit|problematic|target'),
    ('TIMING', r'\bquando\b|\bepoca\b|\bperiodo\b|\bmomento\b|applicazione|impiego'),
    ('CROP', r'coltur'),
    ('N_TREATMENTS', r'trattament|applicazioni'),
    ('NOTES', r'indicazion|note|avvertenz'),
)
RE_DOSE_VALOR = re.compile(
    r'\d+(?:[.,]\d+)?\s*(?:[-–—]\s*\d+(?:[.,]\d+)?\s*)?'
    r'(?:l|kg|g|ml|cc|litri)\s*/\s*(?:ha|hl|100)', re.I)
# a unidade costuma morar no CABEÇALHO: "Dose prodotto (l/ha)" com célula "3 - 5"
RE_UNIDADE_CAB = re.compile(r'\(?\s*(l|kg|g|ml|cc)\s*/\s*(ha|hl)\s*\)?', re.I)
RE_SO_NUMERO = re.compile(r'^\s*\d+(?:[.,]\d+)?\s*(?:[-–—]\s*\d+(?:[.,]\d+)?)?\s*$')


def papel_da_coluna(cabecalho):
    """Que pergunta esta coluna responde. A ordem importa: dose antes de
    tratamento, porque "n° massimo di trattamenti e dose totale" é dose; e
    tempo antes de cultura, pelo motivo escrito acima."""
    t = str(cabecalho or '').lower()
    for papel, padrao in PAPEL_COLUNA:
        if re.search(padrao, t):
            return papel
    return 'UNKNOWN'


def dose_legivel(valor, cabecalho):
    """→ dose com unidade, ou None. A unidade pode estar no cabeçalho.

    "3 - 5" sozinho não é dose: é um número. Com o cabeçalho "Dose prodotto
    (l/ha)" ao lado, passa a ser 3 - 5 l/ha — e a unidade fica dita, não
    subentendida.
    """
    m = RE_DOSE_VALOR.search(valor or '')
    if m:
        return {'VALUE': m.group(0), 'UNIT_FROM': 'CELL'}
    u = RE_UNIDADE_CAB.search(cabecalho or '')
    if u and RE_SO_NUMERO.match(valor or ''):
        return {'VALUE': '%s %s/%s' % (valor.strip(), u.group(1), u.group(2)),
                'UNIT_FROM': 'COLUMN_HEADER'}
    return None


def relacoes_da_tabela(tabela, produto_url):
    """→ relações ANCORADAS. Só nasce par que está na mesma linha.

    Se a tabela não tem coluna de cultura, ela não produz relação de cultura —
    por mais dose que traga. Se não tem coluna de alvo, não produz CROP_ISSUE,
    e é isso que impede o produto cartesiano de entrar por outra porta.
    """
    cab = tabela.get('HEADER') or []
    papeis = [papel_da_coluna(c) for c in cab]
    i_crop = papeis.index('CROP') if 'CROP' in papeis else None
    i_issue = papeis.index('ISSUE') if 'ISSUE' in papeis else None
    saida = {'TABLE_INDEX': tabela.get('TABLE_INDEX'),
             'SECTION_TITLE': tabela.get('SECTION_TITLE'),
             'HEADER': cab, 'COLUMN_ROLES': papeis,
             'HAS_CROP_COLUMN': i_crop is not None,
             'HAS_ISSUE_COLUMN': i_issue is not None,
             'CROP_DOSE': [], 'CROP_ISSUE': [], 'WINDOWS': [], 'PHI': []}
    if i_crop is None:
        saida['WHY_NO_RELATION'] = ('a tabela não tem coluna de cultura; dose sem '
                                    'cultura não vira relação de cultura')
        return saida
    for n, linha in enumerate(tabela.get('ROWS') or []):
        if i_crop >= len(linha):
            continue
        cultura = (linha[i_crop] or '').strip()
        if not cultura:
            continue
        ancora = {'PRODUCT_URL': produto_url,
                  'TABLE_INDEX': tabela.get('TABLE_INDEX'), 'ROW_INDEX': n,
                  'SECTION_TITLE': tabela.get('SECTION_TITLE')}
        for j, papel in enumerate(papeis):
            if j >= len(linha) or j == i_crop:
                continue
            valor = (linha[j] or '').strip()
            if not valor:
                continue
            if papel == 'DOSE':
                d = dose_legivel(valor, cab[j])
                saida['CROP_DOSE'].append(dict(
                    ancora, CROP_AS_WRITTEN=cultura, DOSE_AS_WRITTEN=valor[:300],
                    COLUMN_HEADER=cab[j],
                    DOSE_VALUE_PARSED=d['VALUE'] if d else None,
                    DOSE_UNIT_FROM=d['UNIT_FROM'] if d else None,
                    RELATION_ORIGIN='TABLE_ROW'))
            elif papel == 'ISSUE':
                saida['CROP_ISSUE'].append(dict(
                    ancora, CROP_AS_WRITTEN=cultura, ISSUE_AS_WRITTEN=valor[:300],
                    COLUMN_HEADER=cab[j], RELATION_ORIGIN='TABLE_ROW_SAME_LINE'))
            elif papel == 'TIMING':
                saida['WINDOWS'].append(dict(
                    ancora, CROP_AS_WRITTEN=cultura, WINDOW_AS_WRITTEN=valor[:300],
                    COLUMN_HEADER=cab[j]))
            elif papel == 'PHI':
                saida['PHI'].append(dict(
                    ancora, CROP_AS_WRITTEN=cultura, PHI_AS_WRITTEN=valor[:300],
                    COLUMN_HEADER=cab[j]))
    return saida


# ───────────────────────────────────────── 4 · tipo do documento, pelo conteúdo
ETICHETTA = ai.ETICHETTA
SDS = ai.SCHEDA_SICUREZZA
BROCHURE = ai.BROCHURE
LEAFLET = ai.LEAFLET
ESTENSIONE_USO = 'ESTENSIONE_USO'
COMUNICAZIONE = 'COMUNICAZIONE'
OUTRO = ai.DOC_OUTRO

# Marcas do CONTEÚDO. São frases que o próprio documento carrega, não palpite.
CONTEUDO = (
    (SDS, r'scheda\s+di\s+dati\s+di\s+sicurezza|safety\s+data\s+sheet'),
    (ESTENSIONE_USO, r'estensione\s+d[\'’]?\s*(?:impiego|uso)'),
    (ETICHETTA, r'etichetta\s+autorizzata|decreto\s+dirigenziale'),
)
ROTULO = (
    (ESTENSIONE_USO, r'estension'),
    (ETICHETTA, r'etichett'),
    (SDS, r'scheda\s+di\s+sicurezz|sds'),
    (BROCHURE, r'brochure|depliant'),
    (LEAFLET, r'leaflet|volantino'),
    (COMUNICAZIONE, r'comunicazion'),
)


def _texto_do_pdf(caminho, max_paginas=3, limite=20000):
    """Texto das primeiras páginas, achatado. Sem dependência externa."""
    try:
        import pdf_text
        bruto = pdf_text.text(caminho)
    except Exception:
        return ''
    partes = []

    def achatar(x):
        if isinstance(x, str):
            partes.append(x)
        elif isinstance(x, (list, tuple)):
            for y in x:
                achatar(y)
    if isinstance(bruto, (list, tuple)):
        achatar(bruto[:max_paginas] if bruto and isinstance(bruto[0], (list, tuple))
                else bruto)
    else:
        achatar(bruto)
    return re.sub(r'\s+', ' ', ''.join(partes))[:limite]


def _casa(tabela, texto):
    for tipo, padrao in tabela:
        if re.search(padrao, texto or '', re.I):
            return tipo
    return None


def tipar_documento(doc, raiz=RAIZ):
    """Espécie documental. O conteúdo manda; rótulo e nome ficam ao lado.

    Chamar todo PDF de rótulo foi o defeito nomeado pela missão. O rótulo é ato
    administrativo; a brochura é peça de venda. Aqui os três sinais são medidos
    e a discordância entre eles vira campo, não some.
    """
    caminho = os.path.join(raiz, (doc.get('LOCAL_FILE') or '').replace('/', os.sep))
    texto = _texto_do_pdf(caminho) if os.path.exists(caminho) else ''
    por_conteudo = _casa(CONTEUDO, texto)
    por_rotulo = _casa(ROTULO, doc.get('LABEL_ON_PAGE'))
    por_nome = _casa(ROTULO, doc.get('ORIGINAL_FILENAME'))

    tipo = por_conteudo or por_rotulo or por_nome or OUTRO
    fonte = ('CONTENT' if por_conteudo else
             'LABEL' if por_rotulo else 'FILENAME' if por_nome else 'NONE')
    divergentes = {x for x in (por_conteudo, por_rotulo, por_nome) if x}
    # quantos produtos o próprio documento nomeia no cabeçalho
    cobertos = None
    m = re.search(r'scheda\s+di\s+dati\s+di\s+sicurezza\s+([A-Z0-9®™;,\s\-]{4,90})',
                  texto or '', re.I)
    if m and ';' in m.group(1):
        cobertos = [x.strip() for x in m.group(1).split(';') if x.strip()]
    return {
        'DOCUMENT_TYPE': tipo, 'TYPE_DECIDED_BY': fonte,
        'TYPE_FROM_CONTENT': por_conteudo, 'TYPE_FROM_LABEL': por_rotulo,
        'TYPE_FROM_FILENAME': por_nome,
        'TYPE_SIGNALS_DISAGREE': len(divergentes) > 1,
        'CONTENT_READABLE': bool(texto),
        'PRODUCTS_NAMED_IN_DOCUMENT': cobertos,
        'COVERS_MULTIPLE_PRODUCTS': bool(cobertos and len(cobertos) > 1),
    }


# ─────────────────────────────────────────────────────── 5 · o censo
def identidade(p):
    """A identidade de um produto do catálogo. Nunca o caminho da URL."""
    return p.get('NODE_ID') or p.get('CANONICAL_URL') or p.get('SOURCE_URL')


def censo(arquivo_paginas='amostra-10.json', arquivo_docs='documentos-amostra.json',
          rotulo='AMOSTRA'):
    enum = ler('enumeracao.json', {}) or {}
    pags = (ler(arquivo_paginas, {}) or {}).get('PRODUCTS', [])
    docs = (ler(arquivo_docs, {}) or {}).get('DOCUMENTS', [])
    reg = ai.registro_medido()
    por_id, por_nome = indice_registro(reg)

    ok = [p for p in pags if p.get('STATE') != 'CAPTURE_FAILED']
    por_identidade = {}
    for p in ok:
        por_identidade.setdefault(identidade(p), []).append(p)

    produtos, estados = [], {}
    crop_dose, crop_issue, janelas, phi = [], [], [], []
    cartesiano = 0
    citadas = 0
    for p in ok:
        cw = cruzar(p, por_id, por_nome)
        estados[cw['STATE']] = estados.get(cw['STATE'], 0) + 1
        tabelas = [relacoes_da_tabela(t, p['SOURCE_URL']) for t in (p.get('TABLES') or [])]
        for t in tabelas:
            crop_dose.extend(t['CROP_DOSE'])
            crop_issue.extend(t['CROP_ISSUE'])
            janelas.extend(t['WINDOWS'])
            phi.extend(t['PHI'])
        nc, ni = len(p.get('CROPS') or []), len(p.get('ISSUES') or [])
        cartesiano += nc * ni
        citadas += nc
        produtos.append({
            'PRODUCT_NAME': p.get('PRODUCT_NAME'),
            'PRODUCT_URL': p.get('SOURCE_URL'),
            'CANONICAL_URL': p.get('CANONICAL_URL'),
            'NODE_ID': p.get('NODE_ID'),
            'IDENTITY': identidade(p),
            'URL_PATH_PREFIX': p['SOURCE_URL'].split('/')[5],
            'CATEGORY_DISPLAY': p.get('CATEGORY_DISPLAY'),
            'ACTIVE_INGREDIENT': p.get('ACTIVE_INGREDIENT'),
            'FORMULATION': p.get('FORMULATION'),
            'PACKAGE_SIZE': p.get('PACKAGE_SIZE'),
            'MANUFACTURER_CLAIM_REGISTRATION_ID': p.get('REGISTRATION_ID_AS_WRITTEN'),
            'REGISTRATION_FORMAT_STATE': p.get('REGISTRATION_FORMAT_STATE'),
            'REGISTRATION_ANCHOR_TEXT': p.get('REGISTRATION_ANCHOR_TEXT'),
            'CROSSWALK': cw,
            'CITED_CROPS': nc, 'CITED_ISSUES': ni,
            'CROPS_ARE_SEARCH_LINKS': all(
                '/search?' in (c.get('HREF') or '') for c in (p.get('CROPS') or [])) if nc else None,
            'DECLARED_CROP_RELATIONS': 0,
            'TABLES': tabelas,
            'DOCUMENT_LINKS_ON_PAGE': len(p.get('DOCUMENT_LINKS') or []),
            'ALL_DOCUMENTS_ROUTE': p.get('ALL_DOCUMENTS_LINK'),
            'ALL_DOCUMENTS_ROUTE_STATE': (
                'ROBOTS_DISALLOWED' if p.get('ALL_DOCUMENTS_LINK') else 'ABSENT'),
            'SHA256': p.get('SHA256'), 'LOCAL_FILE': p.get('LOCAL_FILE'),
        })

    # Páginas de SISTEMA ("Rice Cropping Solution") apresentam o rótulo de OUTRO
    # produto. O documento está mesmo na página — e não é do dono dela.
    #     DOCUMENT_ON_PAGE ≠ DOCUMENT_OF_THAT_PRODUCT
    nomes_catalogo = {}
    for p in ok:
        raiz_nome = _nome_chave(p.get('PRODUCT_NAME'))[:7]
        if len(raiz_nome) >= 5:
            nomes_catalogo.setdefault(raiz_nome, set()).add(p.get('PRODUCT_NAME'))

    baixados = [d for d in docs if d.get('STATE') == 'DOWNLOADED']
    docs_medidos, por_tipo, divergem, multi, alheios = [], {}, 0, 0, 0
    for d in baixados:
        t = tipar_documento(d)
        texto_rotulo = _nome_chave(d.get('LABEL_ON_PAGE'))
        dono = _nome_chave(d.get('PRODUCT_NAME'))[:7]
        citados = sorted(r for r in nomes_catalogo if r and r in texto_rotulo)
        de_outro = bool(citados) and dono not in citados
        t['PRODUCT_NAMES_IN_LABEL'] = citados
        t['DOCUMENT_NAMES_ANOTHER_PRODUCT'] = de_outro
        t['ATTRIBUTION'] = ('PRESENTED_ON_PAGE_OF_ANOTHER_PRODUCT' if de_outro
                            else 'PAGE_OWNER')
        por_tipo[t['DOCUMENT_TYPE']] = por_tipo.get(t['DOCUMENT_TYPE'], 0) + 1
        divergem += 1 if t['TYPE_SIGNALS_DISAGREE'] else 0
        multi += 1 if t['COVERS_MULTIPLE_PRODUCTS'] else 0
        alheios += 1 if de_outro else 0
        docs_medidos.append(dict(d, **t))

    # Duas páginas do catálogo podem apontar para UM registro só: a página de
    # sistema herda o número do produto que a compõe.
    #     CATALOG_PRODUCT ≠ REGISTRATION
    por_registro = {}
    for p in produtos:
        cw = p['CROSSWALK']
        if cw['STATE'] == ai.LOCAL_REGISTERED:
            por_registro.setdefault(cw['REGISTRATION_ID'], []).append(p['PRODUCT_NAME'])
    compartilhados = {k: v for k, v in por_registro.items() if len(v) > 1}

    # §18 — só depois da enumeração completa do catálogo. E o nome do campo diz
    # exatamente o que ele é: ausência na superfície pública medida. NÃO diz
    # descontinuado, indisponível, sem importância, nem fora de venda.
    enumeracao_completa = rotulo == 'CENSO_COMPLETO'
    ausentes = None
    if enumeracao_completa:
        casados = set(por_registro)
        ausentes = {
            'CATALOG_ENUMERATION_COMPLETE': True,
            'COUNT': sum(1 for r in reg if r['REGISTRATION_ID'] not in casados),
            'REGISTRATION_IDS': sorted(r['REGISTRATION_ID'] for r in reg
                                       if r['REGISTRATION_ID'] not in casados),
            'WHAT_IT_MEANS': ('esses registros italianos não foram encontrados no '
                              'catálogo público medido em %s' % datetime.date.today()),
            'WHAT_IT_DOES_NOT_MEAN': ['DISCONTINUED', 'UNAVAILABLE', 'NOT_SOLD',
                                      'UNIMPORTANT', 'NOT_REGISTERED'],
            'WHY': ('o catálogo é a vitrine que a empresa escolhe montar; o '
                    'registro é o ato da autoridade. Uma vitrine menor que o '
                    'portfólio é um resultado, não uma falha de coleta'),
        }

    maior = max((d['BYTES'] for d in baixados), default=0)
    hoje = datetime.date.today().isoformat()
    return {
        'CATALOG_ID': 'ITALY_ADAMA_PUBLIC_CATALOG_MEASURED',
        'SCOPE': rotulo,
        'SOURCE_ID': 'IT-ADAMA-CATALOG',
        'SOURCE_COUNTRY': 'IT', 'FACT_COUNTRY': 'IT', 'PORTFOLIO_COUNTRY': 'IT',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'MANUFACTURER_CLAIM',
        'captured_at': hoje, 'CAPTURED_AT': hoje,
        'BROWSER_ROUTE': {
            'STATE': 'HEADED_ONLY',
            'CURL': 'HTTP 403 — 143 bytes',
            'HEADLESS': 'bloqueado — 183 bytes "Access Denied"',
            'HEADED': 'abre — DOM real',
            'WHY': ('a fronteira não é navegador vs. requests: é janela gráfica vs. '
                    'tudo o mais. Planejar coleta em headless devolveria 403 e a '
                    'leitura errada de que o catálogo está vazio'),
        },
        'ROBOTS': {
            'ALLOWS': '/italia/it/',
            'DISALLOWS_USED': ['/italia/en/', '*/ajax/'],
            'CONSEQUENCE': ('a lista "Tutti i documenti" de cada produto vive em '
                            '/italia/it/ajax/product/documents/<id>/nojs e NÃO foi '
                            'buscada. Os documentos medidos são os que a página '
                            'mostra — pode haver mais'),
        },
        'ENUMERATION': {k: enum.get(k) for k in (
            'SITEMAP_LOCS_TOTAL', 'SITEMAP_PRODUCT_URLS', 'HOME_PRODUCT_URLS',
            'UNIQUE_PRODUCT_URLS', 'DUPLICATE_URLS', 'UNCLASSIFIED_URLS',
            'ROBOTS_BLOCKED', 'PATH_PREFIXES', 'CATEGORY_PATHS')},

        'CATALOG_PRODUCT_PAGES': len(ok),
        'CATALOG_PRODUCTS': len(por_identidade),
        'IDENTITY_BASIS': 'NODE_ID do site, com canonical como reserva',
        'PAGES_SHARING_IDENTITY': {k: len(v) for k, v in por_identidade.items()
                                   if len(v) > 1},
        'CAPTURE_FAILED': len(pags) - len(ok),

        'PRODUCTS_WITH_REGISTRATION_CLAIM': sum(
            1 for p in produtos if p['MANUFACTURER_CLAIM_REGISTRATION_ID']),
        'REGISTRATION_FORMAT_STATES': _contar(
            produtos, 'REGISTRATION_FORMAT_STATE'),

        'REGULATORY_PRODUCTS': len(reg),
        'CROSSWALK_STATES': estados,
        'CROSSWALK_REASONS': _contar([p['CROSSWALK'] for p in produtos], 'REASON'),
        'CATALOG_PRODUCTS_SHARING_ONE_REGISTRATION': compartilhados,
        'DISTINCT_REGISTRATIONS_MATCHED': len(por_registro),
        'REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG': ausentes,
        'CROSSWALK_NOTE': ('REGISTERED_BUT_NOT_IN_PUBLIC_CATALOG só é calculado '
                           'quando a enumeração do catálogo está completa; na '
                           'amostra ele sai nulo de propósito'),

        'CITED_CROP_RELATIONS': citadas,
        'DECLARED_CROP_RELATIONS': 0,
        'DECLARED_WHY': ('a página não escreve "autorizzato su X". Ela lista termos '
                         'que são links de busca do site'),
        'CROP_ISSUE_ANCHORED': len(crop_issue),
        'CROP_ISSUE_CARTESIAN_AVOIDED': cartesiano,
        'CROP_DOSE': len(crop_dose),
        'CROP_DOSE_WITH_PARSED_VALUE': sum(1 for x in crop_dose if x['DOSE_VALUE_PARSED']),
        'APPLICATION_WINDOWS': len(janelas),
        'PHI_RELATIONS': len(phi),

        'CATALOG_DOCUMENTS': len(baixados),
        'DOCUMENT_LINKS_SEEN': sum(p['DOCUMENT_LINKS_ON_PAGE'] for p in produtos),
        'DOCUMENTS_BY_TYPE': por_tipo,
        'DOCUMENTS_TYPE_SIGNALS_DISAGREE': divergem,
        'DOCUMENTS_COVERING_MULTIPLE_PRODUCTS': multi,
        'DOCUMENTS_NAMING_ANOTHER_PRODUCT': alheios,
        'LARGEST_ASSET_BYTES': maior,
        'STORAGE_LIMIT_BYTES': 200 * 1024 * 1024,
        'LARGEST_ASSET_WITHIN_LIMIT': maior < 200 * 1024 * 1024,

        'PRODUCTS': produtos,
        'DOCUMENTS': docs_medidos,
        'CROP_DOSE_ROWS': crop_dose,
        'CROP_ISSUE_ROWS': crop_issue,
        'APPLICATION_WINDOW_ROWS': janelas,

        'LAWS': [
            'ADAMA_IT_BROWSER_ROUTE = HEADED_ONLY',
            'ROUTE_BLOCKED ≠ CATALOG_EMPTY',
            'REGISTRATION_ID_FORMAT ≠ REGISTRATION_ID',
            'MENU_TERM ≠ AUTHORIZED_ISSUE',
            'CITED_CROP ≠ AUTHORIZED_CROP',
            'CO_PRESENCE ≠ AUTHORIZED_PAIR',
            'DOSE ≠ CROP_ISSUE_PAIR',
            'LABEL ≠ DOCUMENT_TYPE',
            'ONE DOCUMENT ≠ ONE PRODUCT',
            'DOCUMENT_ON_PAGE ≠ DOCUMENT_OF_THAT_PRODUCT',
            'CATALOG_PRODUCT ≠ REGISTRATION',
            'CLAIM_OUTSIDE_MEASURED_REGISTRY ≠ REGISTRATION_CONFLICT',
            'PATH ≠ IDENTITY',
            'NOME IGUAL ≠ MESMO REGISTRO',
            'HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY',
            'PUBLIC_CATALOG_PRESENCE ≠ REGULATORY_REGISTRATION',
            'REGISTRATION ≠ COMMERCIAL_AVAILABILITY',
            'SESSION ≠ EVIDENCE',
            'RAW PRESENCE ≠ RAW CONTENT VERIFIED',
        ],
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP',
                                     'COMMERCIAL_AVAILABILITY', 'DISCONTINUED'],
        'IMPORT': 'NOT_IN_THIS_MISSION — coleta e importação ficam separadas',
    }


def _contar(itens, campo):
    fora = {}
    for i in itens:
        fora[i.get(campo)] = fora.get(i.get(campo), 0) + 1
    return fora


def main():
    amostra = '--censo' not in sys.argv
    out = (censo() if amostra else
           censo('paginas-produto.json', 'documentos-censo.json', 'CENSO_COMPLETO'))
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    alvo = DESTINO if amostra else DESTINO.replace('MEASURED', 'CENSUS')
    with open(alvo, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('ESCOPO                    :', out['SCOPE'])
    print('CATALOG_PRODUCT_PAGES     :', out['CATALOG_PRODUCT_PAGES'])
    print('CATALOG_PRODUCTS          :', out['CATALOG_PRODUCTS'])
    print('REGULATORY_PRODUCTS       :', out['REGULATORY_PRODUCTS'])
    print('com número publicado      :', out['PRODUCTS_WITH_REGISTRATION_CLAIM'])
    print('CROSSWALK                 :', out['CROSSWALK_STATES'])
    print('CITED_CROP_RELATIONS      :', out['CITED_CROP_RELATIONS'])
    print('DECLARED_CROP_RELATIONS   :', out['DECLARED_CROP_RELATIONS'])
    print('CROP_ISSUE_ANCHORED       :', out['CROP_ISSUE_ANCHORED'])
    print('  cartesiano evitado      :', out['CROP_ISSUE_CARTESIAN_AVOIDED'], 'pares falsos')
    print('CROP_DOSE                 :', out['CROP_DOSE'],
          '(com valor legível:', out['CROP_DOSE_WITH_PARSED_VALUE'], ')')
    print('APPLICATION_WINDOWS       :', out['APPLICATION_WINDOWS'])
    print('CATALOG_DOCUMENTS         :', out['CATALOG_DOCUMENTS'], out['DOCUMENTS_BY_TYPE'])
    print('  sinais discordantes     :', out['DOCUMENTS_TYPE_SIGNALS_DISAGREE'])
    print('  cobrem vários produtos  :', out['DOCUMENTS_COVERING_MULTIPLE_PRODUCTS'])
    print('LARGEST_ASSET_BYTES       :', out['LARGEST_ASSET_BYTES'],
          '(dentro do limite:', out['LARGEST_ASSET_WITHIN_LIMIT'], ')')
    print('->', os.path.relpath(alvo, RAIZ))


if __name__ == '__main__':
    main()
