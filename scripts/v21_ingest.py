#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRÓI O `DESIGN-INGEST/` — o contrato de dado do V2.1.

    python3 scripts/v21_ingest.py

§20 · O OBJETIVO NÃO É PÔR DOIS PACOTES NUM ZIP
------------------------------------------------
É UM contrato. O Design tem de poder escrever

    products = APP.products
    voices   = APP.voices

sem saber qual coleta aconteceu em que noite.

O V2 falhou nisso: `CANONICAL-INTELLIGENCE.json` tinha só os 319 da last-mile,
e o resto ficou em `PREVIOUS-HANDOFF/`. Isso é concatenação de pacote, não fusão.

⚠️ O QUE MUDA EM CADA REGISTRO (§8)
------------------------------------
Todo registro do ingest carrega, sem exceção:

    ID · ENTITY_TYPE · PROVENANCE · QA_STATUS · CLIENT_SAFE (booleano)
    SOURCE_IDS · SOURCE_URLS · REFERENCE_DATE
    CROP_IDS · ISSUE_IDS · REGION_IDS · GEOGRAPHIC_SCOPE

Os campos de pesquisa em português (`o_que`, `valor`, `o_que_nao_prova`)
sobrevivem dentro de `RESEARCH`, porque jogar fora seria perder a origem — mas
o Design NUNCA precisa abrir `RESEARCH` para achar um valor, uma cultura ou uma
data.

    SE O DESIGN TEM DE LER PROSA PARA DESCOBRIR UM FATO, O CONTRATO FALHOU.

⚠️ E A REGRA DO CLIENT_SAFE
----------------------------
    QA_PASS · QA_CORRECTED  → CLIENT_SAFE = true
    QA_UNREVIEWED · QA_REJECTED → CLIENT_SAFE = false

O pacote anterior tem proveniência PRÓPRIA (`REAL_FACT`, `REAL_SOURCE`,
`REAL_DERIVED`), estabelecida antes desta missão. Ela é TRADUZIDA
explicitamente, não rebaixada: um fato lido de documento oficial não vira
`QA_UNREVIEWED` só porque nasceu noutra noite.
"""
import csv
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v21_normalizar as N  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')
ANT = os.path.join(V2, 'PREVIOUS-HANDOFF', '01-DESIGN-READY')
LM = os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE')
ISTAT_CSV = os.path.join(ROOT, 'data', 'samples', 'IT-ISTAT-COLTIVAZIONI',
                         'istat_101_1015_coltivazioni_regioni_2024_2026.csv')
OUT = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1')
ING = os.path.join(OUT, 'DESIGN-INGEST')
ARQ = os.path.join(OUT, 'INTERNAL-ARCHIVE')

# ── as 51 fichas do catálogo, recuperadas do transcrito do coletor ───────────
# ⚠️ A CATEGORIA DA URL NÃO É A CATEGORIA DO PRODUTO.
# Pelo caminho dá 27/13/6/5; pela etiqueta impressa na ficha dá 26/14/6/5.
# O divergente é o Folpan Energy, que mora em /erbicidi/ e a ficha rotula
# «Fungicidi». A etiqueta ganha: ela é o que a ADAMA publica.
CATALOGO_51 = {
    'erbicidi': ['activus-me', 'agil', 'arrodimr', 'clematis', 'contatto-320',
                 'davai', 'dioder', 'edaptisr', 'elegant-2fd', 'folpan-energy',
                 'fullpager-rice-cropping-solution', 'goltix', 'goltixr-top-0',
                 'highcardr', 'leopard-5-ec', 'max-acer-rice-cropping-solution',
                 'nicogan-vo', 'sonavior', 'stopper-p', 'sulcotrek', 'sultan',
                 'taifun-mk-cl', 'taifun-mk-cl-pfnpe', 'timeline-trio', 'tomigan',
                 'trimmer-50-wg', 'valley'],
    'fungicidi': ['avastelr', 'banjo', 'folpan-80-wdg', 'folpan-gold', 'maganicr',
                  'mavita-250-ec', 'maxentisr', 'merpan-80-wdg', 'mirador-sc',
                  'nimrodr-250-ew', 'seedron', 'stavento', 'zakeo-250-sc'],
    'insetticidi': ['apyzar-wg', 'cosayrr-200-sc', 'lamdex-extra', 'mavrik-smart',
                    'pirimor-50', 'schermo-0-5-g'],
    'speciali': ['brevis', 'budge', 'exelgrow', 'parleaf', 'powerfilmr'],
}
CATEGORIA_CORRIGIDA = {'folpan-energy': 'FUNGICIDI'}
TITULAR_OUTRO = {
    'mirador-sc': 'SYNGENTA CROP PROTECTION AG',
    'mavita-250-ec': 'SYNGENTA CROP PROTECTION AG',
    'zakeo-250-sc': 'SYNGENTA CROP PROTECTION AG',
    'timeline-trio': 'SYNGENTA CROP PROTECTION AG',
    'clematis': 'ALBAUGH TKI D.O.O',
    'parleaf': 'MICROCIDE LTD',
}
NAO_FITOSSANITARIO = {'budge': 'n° 0037584/22 (registro de fertilizante)',
                      'exelgrow': 'n. 0023801/18 (registro de fertilizante)'}
SISTEMA_NAO_PRODUTO = {'fullpager-rice-cropping-solution', 'max-acer-rice-cropping-solution'}

# proveniência do pacote anterior → estado de evidência traduzido (§8)
TRADUZ_PROV = {
    'REAL_FACT': ('EVIDENCE_DOCUMENTED', True,
                  'fato lido em documento oficial, com fonte e data. A proveniencia '
                  'foi estabelecida no handoff anterior e e traduzida, nao rebaixada.'),
    'REAL_SOURCE': ('EVIDENCE_SOURCED', True,
                    'registro capturado de fonte publica identificada, com URL e data.'),
    'REAL_DERIVED': ('EVIDENCE_DERIVED', False,
                     'derivacao NOSSA a partir de fatos. Vai a tela so com o metodo '
                     'declarado ao lado — nao sustenta afirmacao sozinha.'),
}


def le(caminho, chave=None):
    if not os.path.exists(caminho):
        return [] if chave else {}
    d = json.load(open(caminho, encoding='utf-8'))
    return (d.get(chave) or []) if chave else d


def ant(rel, chave):
    return le(os.path.join(ANT, rel.replace('/', os.sep)), chave)


def sid(url):
    """ID de fonte estável, derivado do host — o mesmo host, a mesma fonte."""
    m = re.match(r'https?://([^/]+)', str(url or ''))
    h = (m.group(1) if m else 'desconhecida').lower().replace('www.', '')
    return 'SRC_' + re.sub(r'[^A-Z0-9]+', '_', h.upper()).strip('_')[:40]


def base(rid, tipo, prov, qa, urls, data, crops, issues, regions, escopo,
         research=None, extra=None):
    """O envelope obrigatório do §8. Todo registro do ingest passa por aqui."""
    urls = [u for u in (urls if isinstance(urls, list) else [urls]) if u]
    r = {
        'ID': rid,
        'ENTITY_TYPE': tipo,
        'PROVENANCE': prov,
        'QA_STATUS': qa,
        'CLIENT_SAFE': qa in ('QA_PASS', 'QA_CORRECTED', 'EVIDENCE_DOCUMENTED',
                              'EVIDENCE_SOURCED'),
        'SOURCE_IDS': sorted({sid(u) for u in urls}) or ['SRC_NAO_DECLARADA'],
        'SOURCE_URLS': urls,
        'REFERENCE_DATE': data,
        'CROP_IDS': [c for c in (crops or []) if c],
        'ISSUE_IDS': [i for i in (issues or []) if i],
        'REGION_IDS': regions or [],
        'GEOGRAPHIC_SCOPE': escopo or 'NAO_SEI',
    }
    if research:
        r['RESEARCH'] = research
    if extra:
        r.update(extra)
    return r


def do_anterior(x, tipo, urls, data, crops, issues, regions, escopo, extra=None):
    prov = x.get('PROVENANCE') or 'REAL_SOURCE'
    est, safe, porque = TRADUZ_PROV.get(prov, ('EVIDENCE_UNSPECIFIED', False,
                                               'proveniencia nao declarada'))
    r = base(x['ID'], tipo, prov, est, urls, data, crops, issues, regions, escopo,
             extra=extra)
    r['CLIENT_SAFE'] = safe
    r['EVIDENCE_STATUS'] = est
    r['EVIDENCE_STATUS_WHY'] = porque
    r['ORIGIN_LAYER'] = 'PREVIOUS_HANDOFF'
    return r


def do_lastmile(x, tipo, crops=None, issues=None, extra=None):
    reg = N.region_ids(x.get('region'))
    r = base(x['CANONICAL_RECORD_ID'], tipo,
             'REAL_SOURCE_LAST_MILE', x['QA_STATUS'],
             [x.get('source_url')], x.get('publication_date'),
             crops if crops is not None else [N.crop_id(x.get('crop'))],
             issues if issues is not None else [N.issue_id(x.get('crop'), x.get('tipo'))],
             reg, N.escopo(x.get('region'), x.get('geographic_scope')),
             research={
                 'o_que': x.get('o_que'), 'valor': x.get('valor'),
                 'unidade': x.get('unidade'), 'periodo': x.get('periodo'),
                 'o_que_prova': x.get('o_que_prova'),
                 'o_que_nao_prova': x.get('o_que_nao_prova'),
                 'citacao_literal': x.get('citacao_literal'),
                 'IDIOMA': 'pt-BR (nota de pesquisa) · citacao no idioma da fonte',
             }, extra=extra)
    r['ORIGIN_LAYER'] = 'LAST_MILE'
    r['OBSERVATION_CLASS'] = x.get('observation_class') or 'NAO_SEI'
    r['CONFIDENCE'] = x.get('confidence')
    r['SOURCE_SCOPE'] = x.get('source_scope')
    if x.get('RESSALVA_PERMANENTE'):
        r['PERMANENT_CAVEAT'] = x['RESSALVA_PERMANENTE']
    if x.get('QA_O_QUE_MUDOU'):
        r['QA_CHANGED_FIELDS'] = x['QA_O_QUE_MUDOU']
    return r


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(ING)
    os.makedirs(ARQ)

    lm = le(os.path.join(V2, 'CANONICAL-INTELLIGENCE.json'), 'RECORDS')
    por_fam = defaultdict(list)
    for r in lm:
        por_fam[r['FAMILIA']].append(r)

    saidas = {}

    def grava(nome, colecao, itens, chave, verdade, substitui=None, lei=None):
        cs = sum(1 for x in itens if x.get('CLIENT_SAFE'))
        corpo = {
            'COLLECTION': colecao, 'FILE': nome, 'SCHEMA_VERSION': 'V2.1',
            'BUILT_AT': '2026-09-02', 'PRIMARY_KEY': chave,
            'SOURCE_OF_TRUTH': verdade,
            'COUNT_TOTAL': len(itens), 'COUNT_CLIENT_SAFE': cs,
            'BY_ORIGIN': dict(Counter(x.get('ORIGIN_LAYER') for x in itens)),
            'BY_QA': dict(Counter(x.get('QA_STATUS') for x in itens)),
        }
        if substitui:
            corpo['REPLACES_OLD_FILES'] = substitui
        if lei:
            corpo['LAW'] = lei
        corpo['RECORDS'] = itens
        json.dump(corpo, open(os.path.join(ING, nome), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        saidas[colecao] = corpo
        return corpo

    # ══ PRODUTOS REGULATÓRIOS ════════════════════════════════════════════════
    prods = ant('ADAMA/adama-italy-products.json', 'PRODUCTS')
    reg_out = []
    for p in prods:
        reg_out.append(do_anterior(
            p, 'REGULATORY_PRODUCT', [p.get('LABEL_URL')], p.get('EXPIRY'),
            [N.crop_id(c) for c in (p.get('CROP_TERMS_PRESENT') or [])],
            [], ['GEO_ITALY'], 'NACIONAL',
            extra={
                'NAME': p.get('PRODUCT'),
                'REGISTRATION_NUMBER': p.get('REGISTRATION_ID'),
                'AUTHORIZATION_HOLDER': p.get('HOLDER'),
                'ACTIVE_INGREDIENTS': p.get('ACTIVE_INGREDIENTS'),
                'FORMULATION': p.get('FORMULATION'),
                'REGULATORY_CATEGORY': p.get('REGULATORY_CATEGORY'),
                'LINE': p.get('LINE'), 'STATUS': p.get('STATUS'),
                'EXPIRY': p.get('EXPIRY'),
                'MODE_OF_ACTION_DECLARED': p.get('MODE_OF_ACTION_DECLARED'),
                'LABEL_URL': p.get('LABEL_URL'),
                'IN_PUBLIC_CATALOG_FLAG': p.get('IN_PUBLIC_CATALOG'),
            }))
    grava('PRODUCTS-REGULATORY.json', 'PRODUCTS_REGULATORY', reg_out,
          'REGISTRATION_NUMBER',
          'registro do Ministero della Salute · PROD_FTS_6_20260824',
          ['PREVIOUS-HANDOFF/.../ADAMA/adama-italy-products.json',
           'PREVIOUS-HANDOFF/.../ADAMA/adama-{herbicides,fungicides,insecticides,other-lines}.json'],
          'REGULATORY_PRODUCT nao e CATALOG_PRODUCT. Este arquivo e o universo '
          'REGISTRADO com titular ADAMA. O catalogo comercial e outro arquivo, e '
          'os dois nao se somam.')

    # ══ PRODUTOS COMERCIAIS — as 51 fichas ═══════════════════════════════════
    por_nome = {re.sub(r'[^a-z0-9]', '', (p.get('PRODUCT') or '').lower()): p
                for p in prods}
    meu_cat = {re.sub(r'[^a-z0-9]', '', (p.get('NOME_NO_CATALOGO') or '')
                      .replace('®', '').lower()): p
               for p in le(os.path.join(LM, 'IT-ADAMA-CATALOGO.json'), 'PRODUTOS')}

    # ══ AS DUAS CULTURAS QUE SE CHAMAVAM PELO MESMO NOME ═════════════════════
    # `CULTURAS_DECLARADAS_NO_SITE` significava, no dono que a produz, uma coisa
    # só: «em que PÁGINA DE CULTURA cheguei a este produto» — e só sete páginas
    # foram lidas (vite, mais, riso, cereali, pomodoro, pomacee, soia). A jusante
    # ela era lida como «que culturas a ficha do produto declara», e daí como «o
    # produto não pertence a esta cultura».
    #
    #     AUSÊNCIA NO RASTREIO NÃO É AUSÊNCIA NO PRODUTO.
    #
    # O próprio ficheiro do dono já dizia isto, e com todas as letras, em
    # `CULTURA_LEIA_ASSIM`: «chegamos a este produto por link de outra ficha, não
    # por página de cultura. Não ter cultura aqui NÃO significa que ele não
    # tenha.»
    #
    #     A DECLARAÇÃO ESTAVA CERTA. O CONSUMIDOR A JUSANTE É QUE NÃO A LEU.
    #
    # MEDIDO: o censo versionado do catálogo traz 711 pares produto × cultura
    # sobre 149 culturas; o pacote levava 55, sobre 7. Os 656 que faltavam não
    # eram produtos sem cultura: eram produtos a que não se chegou por página.
    #
    # A correcção NÃO funde as duas: separa-as, e cada uma passa a viajar com o
    # nome do que é. A chave da junção é o SLUG DA URL — o nome comercial é
    # escrito de quatro maneiras («Activus® ME», «ACTIVUS ME», «activus-me») e
    # junta 36 de 38; o slug junta 51 de 51.
    censo_por_slug = {}
    _cen = os.path.join(ROOT, 'data', 'samples', 'IT-CATALOGO',
                        'IT-ADAMA-CATALOG-CENSUS-2026-09-02.json')
    if os.path.exists(_cen):
        for _p in (json.load(open(_cen, encoding='utf-8')).get('PRODUCTS') or []):
            censo_por_slug[str(_p.get('URL') or '').rstrip('/').rsplit('/', 1)[-1]
                           .lower()] = _p
    # ── A FICHA DO PRODUTO, LIDA NO SITE ────────────────────────────────────
    # Ate aqui o catalogo entrava so como LISTA: o coletor lia as paginas de
    # CULTURA e extraia os LINKS das fichas. A ficha em si nunca era aberta —
    # e por isso o cartao do portal dizia «principio ativo: nao conhecido» com
    # o dado publicado a um clique de distancia.
    #
    #     TER O ENDERECO NAO E TER LIDO.
    #
    # ADAMA-FICHAS-DE-PRODUTO-V1.json traz as 51 fichas lidas uma a uma no
    # navegador: substancia, formulacao, embalagem, numero de registo, os
    # documentos anexados, e a frase com que a propria ADAMA descreve o
    # produto. Se o ficheiro nao estiver no disco nada disto entra e nada
    # quebra: as chaves ficam None, como ja estavam.
    fichas = {}
    for _f in (le(os.path.join(ROOT, 'data', 'samples', 'IT-LASTMILE',
                               'ADAMA-FICHAS-DE-PRODUTO-V1.json')).get('ITENS') or []):
        fichas[_f.get('SLUG')] = _f

    com_out = []
    for cat, slugs in CATALOGO_51.items():
        for s in slugs:
            fic = fichas.get(s) or {}
            par = fic.get('PAR_CULTURA_ALVO') or {}
            catg = CATEGORIA_CORRIGIDA.get(s, cat.upper())
            nome = re.sub(r'(\w{3,})r$', r'\1', s.replace('-', ' ')).upper().strip()
            chave = re.sub(r'[^a-z0-9]', '', nome.lower())
            reg = por_nome.get(chave)
            det = meu_cat.get(chave, {})
            evid = ['sitemap oficial do adama.com + ficha de produto lida']
            if det:
                evid.append('pagina de cultura do site (leitura independente)')
            # DUAS PERGUNTAS DIFERENTES, DUAS RESPOSTAS QUE NAO SE SOMAM.
            descobertas = list(det.get('CULTURAS_DECLARADAS_NO_SITE') or [])
            fichadocenso = censo_por_slug.get(s)
            declaradas = list((fichadocenso or {}).get('CROPS_DECLARED_ON_PAGE') or [])
            if fichadocenso:
                evid.append('censo do catalogo: a ficha do proprio produto')
            # O termo que o normalizador nao conhece NAO desaparece: fica
            # nomeado. Um vocabulario incompleto e um facto sobre nos, nao
            # sobre o produto.
            nao_reconhecidas = sorted({x for x in declaradas if not N.crop_id(x)})
            com_out.append(base(
                'CATPRD_' + re.sub(r'[^A-Z0-9]+', '_', s.upper()).strip('_'),
                'CATALOG_PRODUCT', 'REAL_SOURCE_LAST_MILE',
                'QA_PASS', ['https://www.adama.com/italia/it/prodotti/%s/%s'
                            % (cat, s)], '2026-09-02',
                sorted({c for c in (
                    [N.crop_id(x) for x in descobertas]
                    + [N.crop_id(x) for x in declaradas]) if c}),
                [], ['GEO_ITALY'], 'NACIONAL',
                extra={
                    'NAME': det.get('NOME_NO_CATALOGO') or nome,
                    'CATEGORY': catg,
                    'CATEGORY_SOURCE': ('etiqueta impressa na ficha (corrige o caminho '
                                        'da URL)' if s in CATEGORIA_CORRIGIDA
                                        else 'caminho da URL, confirmado pela ficha'),
                    'PUBLIC_CATALOG_URL': 'https://www.adama.com/italia/it/prodotti/%s/%s'
                                          % (cat, s),
                    'CROPS_DECLARED_BY_PRODUCT': declaradas,
                    'CROPS_DISCOVERED_VIA_CROP_PAGE': descobertas,
                    'CROPS_NOT_RECOGNISED': nao_reconhecidas,
                    'CROPS_NOT_RECOGNISED_COUNT': len(nao_reconhecidas),
                    'CROP_DECLARATION_STATE': (
                        'DECLARED_BY_PRODUCT' if declaradas else
                        'DISCOVERED_VIA_CROP_PAGE_ONLY' if descobertas else
                        'UNKNOWN'),
                    'CROP_SEMANTICS_LAW':
                        'CROPS_DECLARED_BY_PRODUCT e o que a FICHA DO PRODUTO '
                        'declara. CROPS_DISCOVERED_VIA_CROP_PAGE e por que '
                        'PAGINA DE CULTURA chegamos a ele, e so sete paginas '
                        'foram lidas. NAO TER SIDO ENCONTRADO POR UMA PAGINA '
                        'NAO E O PRODUTO NAO TER A CULTURA. As duas listas '
                        'nunca se somam num numero so, e CROP_IDS e a UNIAO '
                        'delas — nao a segunda sozinha, como era ate aqui.',
                    'ACTIVE_INGREDIENTS': (det.get('ATIVOS_NA_PAGINA')
                                           or fic.get('ACTIVE_INGREDIENTS_ON_SITE')),
                    'REGISTRATION_NUMBER_ON_PAGE': (det.get('REGISTRO_NA_PAGINA')
                                                    or fic.get('REGISTRATION_ON_SITE_LITERAL')),
                    # o que a ficha do proprio produto publica, lido em 07/09/2026
                    'FORMULATION_ON_PAGE': fic.get('FORMULATION_ON_SITE'),
                    'PACKAGE_SIZES_ON_PAGE': fic.get('PACKAGE_SIZES'),
                    'PRODUCT_DOCUMENT_URLS': fic.get('DOCUMENT_URLS'),
                    'PRODUCT_DESCRIPTOR_ON_SITE': fic.get('DESCRITOR_DO_SITE'),
                    # ── PORQUE E QUE ESTE CARTAO PODE ESTAR VAZIO ───────────
                    # Um cartao vazio nao diz porque esta vazio, e ha duas
                    # razoes que nao se parecem nada uma com a outra:
                    #   · ainda nao colhemos / o leitor nao achou a tabela;
                    #   · nao ha o que colher, porque o produto nao actua
                    #     sobre organismo nenhum — biostimulante, coadiuvante,
                    #     bagnante ou diradante.
                    # A segunda nao e uma lacuna: e a resposta certa. Sao cinco
                    # dos 51, e quem os classifica e a ADAMA, na frase que
                    # escreveu na propria ficha. A regra nao e nossa.
                    #
                    #     VAZIO SEM MOTIVO PARECE DIVIDA. COM MOTIVO, E FACTO.
                    'CROP_TARGET_PAIR_STATE': par.get('ESTADO'),
                    'CROP_TARGET_PAIR_WHY': par.get('PORQUE'),
                    'CROP_TARGET_PAIR_CLASSIFIED_BY': par.get('FONTE_DA_CLASSIFICACAO'),
                    'REGISTRY_CROSS_CHECK': fic.get('CROSS_CHECK_REGISTO'),
                    'CATALOG_EVIDENCE': evid,
                    'CATALOG_STATUS': 'PUBLISHED',
                    'AUTHORIZATION_HOLDER': TITULAR_OUTRO.get(s) or (
                        reg.get('HOLDER') if reg else None),
                    'HOLDER_IS_ADAMA': None if s in TITULAR_OUTRO else bool(reg),
                    'MATCHED_REGULATORY_ID': reg.get('REGISTRATION_ID') if reg else None,
                    'NOT_A_PLANT_PROTECTION_PRODUCT': NAO_FITOSSANITARIO.get(s),
                    'IS_SYSTEM_NOT_PRODUCT': s in SISTEMA_NAO_PRODUTO,
                    'COMMERCIAL_CONTRACT': 'UNKNOWN',
                    'COMMERCIAL_CONTRACT_WHY':
                        'titular de autorizacao NAO e vendedor. A presenca no catalogo '
                        'nao revela o contrato, e o contrato nao se infere.',
                }))
    grava('PRODUCTS-COMMERCIAL.json', 'PRODUCTS_COMMERCIAL', com_out,
          'ID', 'catalogo publico adama.com/italia · sitemap + 51 fichas',
          ['V2/COMMERCIAL-CATALOG.json (eram 10 ACHADOS, nao produtos)'],
          'CATALOG_PRODUCT nao e REGULATORY_PRODUCT. Seis destes tem autorizacao em '
          'nome de OUTRA empresa; dois nem sao fitossanitarios. Titular nao e '
          'vendedor, e o contrato comercial permanece UNKNOWN.')

    # ══ RELAÇÕES DE PRODUTO — 2.030 pares + 219 linhas ══════════════════════
    pares = ant('LABEL-USE/label-use-pairs.json', 'PAIRS')
    rel_out = []
    for p in pares:
        rel_out.append(do_anterior(
            p, 'LABEL_USE_RELATIONSHIP', [], None,
            [N.crop_id(p.get('CROP'))], [N.issue_id(p.get('TARGET'),
                                                    p.get('TARGET_AS_WRITTEN_ON_LABEL'))],
            ['GEO_ITALY'], 'NACIONAL',
            extra={
                'PRODUCT_NAME': p.get('PRODUCT'),
                'REGISTRATION_NUMBER': p.get('REGISTRATION_ID'),
                'CROP_ON_LABEL': p.get('CROP'),
                'TARGET_ON_LABEL': p.get('TARGET'),
                'TARGET_AS_WRITTEN': p.get('TARGET_AS_WRITTEN_ON_LABEL'),
                'TARGET_KIND': p.get('TARGET_KIND'),
                'WEED_GROUP': p.get('WEED_GROUP'),
                'LINK_STRENGTH': p.get('LINK_STRENGTH'),
                'LINK_MEANS': p.get('LINK_MEANS'),
                'QUOTE_FROM_LABEL': p.get('QUOTE_FROM_LABEL'),
                'WHAT_IT_DOES_NOT_PROVE': p.get('WHAT_IT_DOES_NOT_PROVE'),
            }))
    grava('PRODUCT-RELATIONSHIPS.json', 'PRODUCT_RELATIONSHIPS', rel_out,
          'ID', 'rotulo autorizado do Ministero, lido por dentro',
          ['PREVIOUS-HANDOFF/.../LABEL-USE/label-use-pairs.json',
           'PREVIOUS-HANDOFF/.../ADAMA/adama-crop-problem-product.json'],
          'as tres forcas de ligacao NAO SE SOMAM: LINHA_DA_TABELA e '
          'BLOCO_DA_CULTURA sao o documento unindo cultura e alvo; '
          'DECLARACAO_DE_PRODUTO somos nos aproximando duas listas separadas.')

    json.dump({'_': 'placeholder — o resto e escrito por v21_ingest_b.py'},
              open(os.path.join(ING, '_PARCIAL.json'), 'w', encoding='utf-8'))

    print('parte A escrita:')
    for k, v in saidas.items():
        print('  %-24s %5d total · %5d client-safe' %
              (k, v['COUNT_TOTAL'], v['COUNT_CLIENT_SAFE']))


if __name__ == '__main__':
    main()
