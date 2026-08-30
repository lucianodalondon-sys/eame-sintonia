#!/usr/bin/env python3
"""
CENSO ITALIANO — os números MEDIDOS, e a porta que não abriu.

A Itália não tenta "bater" com os 56 da Espanha. São países independentes, e o
que sai daqui é contagem, não meta.

O QUE ESTÁ MEDIDO
------------------
O lado AUTORIDADE, por inteiro: 163 registros ADAMA no banco do Ministero della
Salute, com número, titular, substância, vencimento e etiqueta — e as etiquetas
foram obtidas, 163 de 163.

O QUE NÃO ESTÁ
---------------
O lado CATÁLOGO. A adama.com devolve 403 a tudo que sai deste contêiner,
inclusive ao `robots.txt` — não é uma rota errada, é bloqueio uniforme. A Espanha
passou pelo mesmo e resolveu do único jeito legítimo: o navegador local do
usuário trouxe as páginas. É o que a Itália precisa, e o handoff diz exatamente
o quê.

    ROUTE_BLOCKED ≠ CATALOG_EMPTY

E POR ISSO O CROSSWALK ESTÁ PRONTO E VAZIO
--------------------------------------------
Os quatro estados existem, são testados, e nenhum produto está em nenhum deles —
porque o crosswalk precisa dos DOIS lados e só um chegou. Um crosswalk com zero
linhas e o contrato provado é honesto; um crosswalk preenchido a partir de um
lado só seria o defeito que a Espanha nomeou primeiro.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import adama_it as ai       # noqa: E402
import adama_it_raw as rw   # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CATALOGO',
                    'IT-ADAMA-CATALOG-V1.json')


CASO = 'IT-CASE-DURUM-FUSARIUM-001'


def round_trip_do_caso():
    """§27 — o caso atravessa o censo, e o censo não fecha o caso.

    Procura os produtos cujo rótulo traz o TERMO da cultura do caso e o TERMO do
    problema do caso. Co-presença, e nada além disso.

    E o resultado carrega o próprio aviso: em três dos seis, o alvo aparece no
    rótulo como **"Triticale Fusariosi"** — a fusariose ali está amarrada ao
    TRITICALE, não ao grano duro. Se co-presença fechasse par, esses três
    virariam uma afirmação de que o produto é autorizado contra fusariose em
    trigo duro. O rótulo não diz isso.

        CO_PRESENCE ≠ AUTHORIZED_PAIR
    """
    prods = ai.registro_medido()
    duro = [p for p in prods if 'DURUM_WHEAT' in (p.get('CROP_TERMS_PRESENT') or [])]
    achados = []
    for p in duro:
        for i in (p.get('ISSUES_FROM_SOURCE') or []):
            rotulo = i.get('ISSUE_VERNACULAR_IT') or ''
            sci = i.get('SCIENTIFIC_NAME') or ''
            if 'fusari' in (rotulo + ' ' + sci).lower():
                achados.append({
                    'PRODUCT': p['PRODUCT'],
                    'REGISTRATION_ID': p['REGISTRATION_ID'],
                    'ISSUE_LABEL_AS_WRITTEN': rotulo,
                    'SCIENTIFIC_NAME': sci,
                    'ISSUE_TERM_BOUND_TO_ANOTHER_CROP': rotulo.lower().startswith(
                        ('triticale', 'orzo', 'avena', 'segale')),
                    'PAIR_STATE': 'CO_PRESENCE_ONLY_NOT_AUTHORIZED_PAIR',
                })
                break
    amarrados = [a for a in achados if a['ISSUE_TERM_BOUND_TO_ANOTHER_CROP']]
    return {
        'CASE_ID': CASO,
        'CROP_TERM': 'DURUM_WHEAT', 'ISSUE_TERM': 'fusariosi',
        'PRODUCTS_WITH_CROP_TERM': len(duro),
        'PRODUCTS_WITH_BOTH_TERMS': len(achados),
        'PRODUCTS': achados,
        'ISSUE_TERM_BOUND_TO_ANOTHER_CROP': len(amarrados),
        'WHAT_THIS_IS': ('co-presença de termos no mesmo rótulo — o produto '
                         'aparece no censo e o caso é reencontrado'),
        'WHAT_THIS_IS_NOT': (
            'autorização de uso contra fusariose em trigo duro. Em %d dos %d, o '
            'alvo está escrito como "Triticale Fusariosi": a fusariose ali é do '
            'TRITICALE. Fechar o par por co-presença inventaria uma autorização '
            'que o rótulo não dá' % (len(amarrados), len(achados))),
        'WHAT_WOULD_CLOSE_IT': 'a tabela cultura↔alvo↔dose do PDF da etiqueta',
    }


def censo():
    prods = ai.registro_medido()
    with open(os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                           'IT-T4-001-etichette-manifest.json'), encoding='utf-8') as fh:
        man = json.load(fh)

    relacoes, por_origem = [], {}
    issues_total, com_bbch = 0, 0
    for p in prods:
        for r in ai.relacoes_de_cultura(p):
            relacoes.append(r)
            por_origem[r['RELATION_ORIGIN']] = por_origem.get(r['RELATION_ORIGIN'], 0) + 1
        issues_total += len(p.get('ISSUES_FROM_SOURCE') or [])

    cartesiano = sum(len(p.get('CROP_TERMS_PRESENT') or []) *
                     len(p.get('ISSUES_FROM_SOURCE') or []) for p in prods)

    substancias = sorted({p.get('ACTIVE_SUBSTANCE') for p in prods if p.get('ACTIVE_SUBSTANCE')})
    estados_extracao = {}
    for p in prods:
        e = p.get('EXTRACTION_STATE') or 'NÃO SEI'
        estados_extracao[e] = estados_extracao.get(e, 0) + 1

    hoje = datetime.date.today().isoformat()
    return {
        'CATALOG_ID': 'ITALY_ADAMA_LOCAL_CATALOG_V1',
        'SOURCE_ID': 'DERIVED/IT-ADAMA-CATALOG-V1',
        'source': 'registro do Ministero (medido) + catálogo ADAMA (bloqueado)',
        'SOURCE_COUNTRY': 'IT', 'FACT_COUNTRY': 'IT', 'PORTFOLIO_COUNTRY': 'IT',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'captured_at': hoje, 'CAPTURED_AT': hoje,

        'SOURCES': {'REGULATORY': ai.FONTE_REGULATORIA, 'CATALOG': ai.FONTE_CATALOGO},
        'CATALOG_ROUTE_STATE': {
            'STATE': 'ROUTE_BLOCKED_WAF',
            'MEASURED': ['/italia/it 403', '/italia/it/prodotti 403',
                         '/italy/en 403', '/robots.txt 403'],
            'WHY_NOT_EMPTY': ('403 uniforme, inclusive no robots.txt, é bloqueio de '
                              'borda — não diz nada sobre o conteúdo do catálogo'),
            'PRECEDENT': ('a Espanha teve o mesmo 403 e resolveu pelo navegador local '
                          'do usuário; o código dela diz textualmente que o PDF da '
                          'ADAMA só chega pelo navegador'),
        },

        # ── o que está medido ────────────────────────────────────────────────
        'PRODUCTS_REGULATORY': len(prods),
        'PRODUCTS_CATALOG': 0,
        'PRODUCTS_CATALOG_STATE': 'NOT_COLLECTED_ROUTE_BLOCKED',
        'DOCUMENTS_REGULATORY': man.get('LABELS_OBTAINED', len(prods)),
        'DOCUMENTS_BY_TYPE': {ai.ETICHETTA: man.get('LABELS_OBTAINED', len(prods))},
        'DOCUMENTS_CATALOG': 0,
        'ACTIVE_SUBSTANCES': len(substancias),
        'HOLDER_ENTITIES': ai.HOLDER_ENTITIES_MEASURED,
        'EXTRACTION_STATES': estados_extracao,

        'CROP_RELATIONS': len(relacoes),
        'CROP_RELATIONS_BY_ORIGIN': por_origem,
        'DECLARED': por_origem.get(ai.CROP_DECLARED, 0),
        'CITED': por_origem.get(ai.CROP_CITED, 0),
        'AUTHORIZED_REGULATORY': por_origem.get(ai.CROP_REGULATORY, 0),
        'ROTATION_ONLY': por_origem.get(ai.CROP_ROTATION_ONLY, 0),

        'ISSUES_FROM_SOURCE': issues_total,
        'CROP_ISSUE': 0,
        'CROP_ISSUE_STATE': 'NOT_RECONSTRUCTED_FROM_SOURCE',
        'CROP_ISSUE_CARTESIAN_AVOIDED': cartesiano,
        'CROP_ISSUE_WHY': ('a tabela cultura↔alvo do PDF não foi reconstruída. Cruzar '
                           'as listas produziria %d pares que ninguém autorizou'
                           % cartesiano),

        'CROP_DOSE': 0,
        'CROP_DOSE_STATE': 'NOT_EXTRACTED — a dose por cultura vive na tabela do PDF',
        'WINDOWS': 0,
        'WINDOWS_STATE': 'NOT_EXTRACTED — depende da mesma tabela',

        # ── crosswalk: contrato pronto, zero linhas ──────────────────────────
        'CROSSWALK': {
            'STATES_AVAILABLE': [ai.LOCAL_REGISTERED, ai.LOCAL_PRESENT_NOT_PROVED,
                                 ai.REGISTRATION_CONFLICT, ai.REGISTERED_NOT_IN_CATALOG,
                                 ai.NOT_REGISTERED, ai.CROSSWALK_NOT_KNOWN],
            'ROWS': 0,
            'LOCAL_REGISTERED': 0,
            'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED': 0,
            'REGISTRATION_CONFLICT': 0,
            'WHY_ZERO': ('o crosswalk precisa dos dois lados e só o regulatório '
                         'chegou. Preenchê-lo a partir de um lado seria inventar '
                         'a metade que falta'),
        },

        # ── RAW ──────────────────────────────────────────────────────────────
        'RAW': {
            'PLAN_EXISTS_FROM_DAY_ONE': True,
            'PIPELINE': ['DOWNLOAD', 'LOCAL_SHA256', 'METADATA', 'RAW_PLAN',
                         'STORAGE_KEY', 'UPLOAD', 'REMOTE_INVENTORY',
                         'DOWNLOAD_BACK', 'SHA_VERIFY'],
            'RAW_EXPECTED': 0, 'RAW_REMOTE_PRESENT': 0,
            'RAW_CONTENT_HASH_VERIFIED': 0, 'HASH_MISMATCH': 0,
            'ORPHANS': 0, 'FAILED': 0,
            'LARGEST_ASSET_MEASURED': rw.LIMITE_A_MEDIR['STATE'],
            'GATE': rw.gate(esperado=0, remoto_presente=0, remoto_ausente=0,
                            orfaos=0, falhos=0, hash_conferido=0, hash_divergente=0),
        },

        'LAWS': [
            'PORTFÓLIO GLOBAL ≠ PORTFÓLIO LOCAL ITÁLIA',
            'PUBLIC_CATALOG_PRESENCE ≠ REGULATORY_REGISTRATION',
            'REGISTRATION ≠ COMMERCIAL_AVAILABILITY',
            'LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED ≠ NOT_REGISTERED',
            'CAPTURE ≠ REGISTRATION',
            'NOME IGUAL ≠ MESMO REGISTRO',
            'DECLARED_CROP ≠ CITED_CROP ≠ AUTHORIZED_CROP',
            'DOSE ≠ CROP_ISSUE_PAIR',
            'MENU_TERM ≠ AUTHORIZED_ISSUE',
            'PATH ≠ IDENTITY',
            'RAW PRESENCE ≠ RAW CONTENT VERIFIED',
            'HTTP_5XX ≠ OBJECT_NOT_PRESERVED',
            'HOLDER_COUNTRY ≠ REGISTRATION_COUNTRY ≠ PORTFOLIO_COUNTRY',
            'ROUTE_BLOCKED ≠ CATALOG_EMPTY',
        ],

        'HANDOFF': {
            'WHAT_THE_LOCAL_BROWSER_MUST_BRING': [
                'a página de listagem do catálogo ADAMA Italia, HTML salvo inteiro',
                'a paginação completa, ou o parâmetro que a derruba de uma vez',
                'uma página de produto por categoria, para o schema',
                'os PDFs que as páginas de produto linkarem, com o nome original',
                'um índice JSON: URL → arquivo salvo → content-type → bytes',
            ],
            'WHY_THIS_SHAPE': ('é o mesmo formato que a Espanha usou — '
                               'data/raw/ES/adama-website/documentos-baixados.json —, '
                               'e o parser italiano já sabe consumi-lo'),
            'DESTINATION': 'data/raw/IT/adama-website/',
            'WHAT_HAPPENS_NEXT': ('o parser tipa documentos, o crosswalk cruza com os '
                                  '163 registros, e o RAW sobe com hash conferido'),
        },

        'CASE_ROUND_TRIP': round_trip_do_caso(),

        'ITALY_CATALOG_HANDOFF_READY': 'YES',
        'RAW_PRESERVATION_GATE_IT': 'OPEN',
        'CATALOG_SIDE_STATE': 'NOT_COLLECTED_ROUTE_BLOCKED',
        'REGULATORY_SIDE_STATE': 'MEASURED_COMPLETE',
        'IMPORT': 'NOT_IN_THIS_MISSION — coleta e importação ficam separadas',
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP',
                                     'COMMERCIAL_AVAILABILITY'],
    }


def main():
    out = censo()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('LADO REGULATÓRIO  —', out['REGULATORY_SIDE_STATE'])
    print('  PRODUCTS        :', out['PRODUCTS_REGULATORY'])
    print('  DOCUMENTS       :', out['DOCUMENTS_REGULATORY'], '(todas ETICHETTA)')
    print('  ACTIVE_SUBST    :', out['ACTIVE_SUBSTANCES'])
    print('  titulares       :', out['HOLDER_ENTITIES'])
    print('  CROP_RELATIONS  :', out['CROP_RELATIONS'], out['CROP_RELATIONS_BY_ORIGIN'])
    print('  ISSUES          :', out['ISSUES_FROM_SOURCE'])
    print('  CROP_ISSUE      :', out['CROP_ISSUE'], '—', out['CROP_ISSUE_STATE'])
    print('  cartesiano evitado:', out['CROP_ISSUE_CARTESIAN_AVOIDED'], 'pares falsos')
    print()
    print('LADO CATÁLOGO     —', out['CATALOG_SIDE_STATE'])
    print('  rota            :', out['CATALOG_ROUTE_STATE']['STATE'])
    print('  medido          :', ', '.join(out['CATALOG_ROUTE_STATE']['MEASURED']))
    print()
    print('CROSSWALK rows    :', out['CROSSWALK']['ROWS'], '—', out['CROSSWALK']['WHY_ZERO'][:60])
    print('RAW gate          :', out['RAW']['GATE']['STATE'])
    print('  faltam          :', ', '.join(out['RAW']['GATE']['MISSING']))
    print()
    rt = out['CASE_ROUND_TRIP']
    print('ROUND-TRIP do caso:', rt['PRODUCTS_WITH_CROP_TERM'], 'com termo da cultura,',
          rt['PRODUCTS_WITH_BOTH_TERMS'], 'com os dois termos,',
          rt['ISSUE_TERM_BOUND_TO_ANOTHER_CROP'], 'com o alvo preso a OUTRA cultura')
    for a in rt['PRODUCTS']:
        print('   %-16s %-8s %-22s outro-crop=%s' % (
            a['PRODUCT'][:16], a['REGISTRATION_ID'], a['ISSUE_LABEL_AS_WRITTEN'][:22],
            a['ISSUE_TERM_BOUND_TO_ANOTHER_CROP']))
    print()
    print('ITALY_CATALOG_HANDOFF_READY =', out['ITALY_CATALOG_HANDOFF_READY'])
    print('RAW_PRESERVATION_GATE_IT    =', out['RAW_PRESERVATION_GATE_IT'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
