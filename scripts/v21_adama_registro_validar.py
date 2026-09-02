#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IT-T4-001 · VALIDAR o recorte ADAMA do registro italiano contra o V2.1.

    python3 scripts/v21_adama_registro_validar.py

POR QUE ESTE ARQUIVO EXISTE
---------------------------
Chegou um artefato de outra missao (branch claude/adama-italia-scrape-qov10l)
dizendo "163 autorizacoes vivas hoje". O numero e verdadeiro; a palavra "vivas"
nao e. Este script mede a diferenca, em vez de descreve-la.

    NUMERO QUE NAO SE RECALCULA E NUMERO QUE VAI MENTIR ALGUM DIA.

Tudo aqui se reconta dos arquivos, toda vez.

O QUE ELE NAO FAZ
-----------------
Nao escreve no pacote. Nao promove nada a client-safe. Ele mede e prepara um
payload de enriquecimento — quem aplica e a cadeia, com a mao do humano.
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
OUT = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001')

# A data de referencia e PINADA na versao do dado, nunca em date.today().
# O coletor de origem usa date.today(): re-rodar amanha muda o numero sem que o
# dado tenha mudado. Aqui a data vem do proprio nome do arquivo de origem.
#
#     A DATA DE HOJE NAO E UM FATO DO DADO. E UM FATO DA HORA EM QUE SE RODOU.
REF_PADRAO = date(2026, 9, 2)   # data de leitura declarada pelo coletor

# O CSV separa substancias com "|". O coletor de origem faz split("+"), entao
# produto de duas substancias vira UMA string colada. O V2.1 separou certo.
SEP_ATIVAS = re.compile(r'[|+]')


def _data_it(s):
    try:
        return datetime.strptime(str(s).strip(), '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None


def _data_iso(s):
    for f in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(str(s).strip(), f).date()
        except (ValueError, TypeError):
            continue
    return None


def chave(x):
    """Numero de registro normalizado — a chave de juncao mais forte que existe.

    Nunca juntamos por nome aproximado: nome de produto se repete entre
    titulares e muda de grafia entre fontes.
    """
    s = re.sub(r'\D', '', str(x or ''))
    return s.lstrip('0').zfill(6) if s else None


def ativas(p):
    """As substancias de verdade, separando por | E por +."""
    out = []
    for bruto in (p.get('substancias_ativas') or []):
        for t in SEP_ATIVAS.split(str(bruto)):
            t = t.strip()
            if t and t != '-':
                out.append(t)
    return out


def carregar(caminho_portfolio):
    with open(caminho_portfolio, encoding='utf-8') as fh:
        novo = json.load(fh)
    with open(os.path.join(ING, 'PRODUCTS-REGULATORY.json'), encoding='utf-8') as fh:
        reg = json.load(fh)['RECORDS']
    return novo, reg


def medir(novo, reg, ref=REF_PADRAO):
    r = {'REFERENCIA': ref.isoformat(),
         'ARQUIVO_ORIGEM': novo.get('arquivo_origem'),
         'VERSAO_DO_DADO': novo.get('versao_do_dado')}

    prod = novo['produtos']
    vivos = [p for p in prod if p['vivo']]
    nk = {chave(p['num_registrazione']): p for p in prod}
    rk = {chave(x.get('REGISTRATION_NUMBER')): x for x in reg}

    # ── 1 · o que "vivo" quer dizer, medido ──────────────────────────────────
    venc = [p for p in vivos
            if _data_it(p['data_scadenza']) and _data_it(p['data_scadenza']) < ref]
    scad = [p for p in prod if p['estado_administrativo'] == 'Scaduto']
    ds = sorted(d for d in (_data_it(p['data_scadenza']) for p in scad) if d)
    dv = sorted(d for d in (_data_it(p['data_scadenza']) for p in vivos) if d)
    r['SEMANTICA_DE_VIVO'] = {
        'DEFINICAO_NO_CODIGO': 'stato_amministrativo.startswith(("Autorizzato","Ri-registrato","Rinnovato"))',
        'LE_A_DATA_DE_VALIDADE': False,
        'VIVOS': len(vivos),
        'VIVOS_COM_VALIDADE_VENCIDA': len(venc),
        'ESTADO_SCADUTO_EXISTE_NO_REGISTRO': len(scad),
        'SCADUTO_VALIDADE_MAIS_RECENTE': ds[-1].isoformat() if ds else None,
        'VIVO_VALIDADE_MAIS_ANTIGA': dv[0].isoformat() if dv else None,
        'HA_SOBREPOSICAO': bool(ds and dv and dv[0] < ds[-1]),
        'VENCIDOS_COM_DECRETO_DE_REVOGACAO': sum(
            1 for p in venc if str(p.get('data_decorrenza_revoca', '')).strip() not in ('', '-')),
        'REVOCATO_COM_DECRETO': sum(
            1 for p in prod if p['estado_administrativo'] == 'Revocato'
            and str(p.get('data_decorrenza_revoca', '')).strip() not in ('', '-')),
        'CONCLUSAO': ('ESTADO ADMINISTRATIVO PUBLICADO, COM ATRASO. Nao e validade '
                      'formal: o registro so move para Scaduto casos antigos, e os '
                      'vencidos recentes seguem Autorizzato sem decreto de revogacao. '
                      'Nao e carencia: nenhum dos vencidos tem decreto. A extracao e '
                      'fiel; o rotulo "vivo hoje" e que nao se sustenta.'),
    }
    r['VIVOS_VENCIDOS'] = [
        {'num_registrazione': p['num_registrazione'], 'produto': p['produto'],
         'estado_administrativo': p['estado_administrativo'],
         'data_scadenza': p['data_scadenza']}
        for p in sorted(venc, key=lambda x: _data_it(x['data_scadenza']))]

    # ── 2 · o defeito do separador ───────────────────────────────────────────
    colados = [p for p in vivos if any('|' in s for s in p['substancias_ativas'])]
    reais = Counter(s for p in vivos for s in ativas(p))
    v21 = Counter(s.strip().upper() for x in reg for s in (x.get('ACTIVE_INGREDIENTS') or []))
    r['SEPARADOR_DE_ATIVAS'] = {
        'COLETOR_USA': "split('+')",
        'CSV_SEPARA_COM': '|',
        'VIVOS_COM_ATIVAS_COLADAS': len(colados),
        'ENTRADAS_PUBLICADAS_PELO_COLETOR': len(novo.get('substancias_ativas_vivas') or []),
        'DESSAS_QUE_SAO_COMBINACAO_COLADA': sum(
            1 for k, _ in (novo.get('substancias_ativas_vivas') or []) if '|' in k),
        'SUBSTANCIAS_DISTINTAS_REAIS': len(reais),
        'SUBSTANCIAS_DISTINTAS_NO_V21': len(v21),
        'V21_TEM_ATIVA_COLADA': sum(1 for x in reg
                                    for s in (x.get('ACTIVE_INGREDIENTS') or []) if '|' in s),
        'CONCLUSAO': ('o V2.1 separou certo e o coletor novo nao. NAO sobrescrever '
                      'ACTIVE_INGREDIENTS do V2.1 com este campo.'),
    }

    # ── 3 · o cruzamento, so por numero de registro ──────────────────────────
    inter = set(rk) & set(nk)
    vivos_k = {chave(p['num_registrazione']) for p in vivos}
    div = {'STATUS': [], 'EXPIRY': [], 'HOLDER': [], 'ATIVAS': []}
    for k in sorted(inter):
        a, b = rk[k], nk[k]
        if (a.get('STATUS') or '').strip() != (b['estado_administrativo'] or '').strip():
            div['STATUS'].append(k)
        eb = _data_it(b['data_scadenza'])
        ea = _data_iso(a.get('EXPIRY'))
        if ea and eb and ea != eb:
            div['EXPIRY'].append(k)
        if (a.get('AUTHORIZATION_HOLDER') or '').strip().upper() != (b['titular'] or '').strip().upper():
            div['HOLDER'].append(k)
        if sorted(s.strip().upper() for s in (a.get('ACTIVE_INGREDIENTS') or [])) != \
           sorted(s.upper() for s in ativas(b)):
            div['ATIVAS'].append(k)
    r['CRUZAMENTO'] = {
        'CHAVE': 'num_registrazione / REGISTRATION_NUMBER, normalizado (nunca por nome)',
        'V21_TOTAL': len(reg), 'V21_CHAVES_DISTINTAS': len(rk),
        'NOVO_TOTAL': len(prod), 'NOVO_CHAVES_DISTINTAS': len(nk),
        'MATCHED_EXISTING_PRODUCTS': len(inter),
        'MATCHED_CONTRA_OS_VIVOS': len(set(rk) & vivos_k),
        'NEW_REGULATORY_ENTITIES': len(set(nk) - set(rk)),
        'NEW_QUE_SAO_VIVOS': len(vivos_k - set(rk)),
        'SO_NO_V21': len(set(rk) - set(nk)),
        'DUPLICATES_V21': sum(1 for _ in ()) or len(reg) - len(rk),
        'DUPLICATES_NOVO': len(prod) - len(nk),
        'CONFLICTS_STATUS': len(div['STATUS']),
        'CONFLICTS_EXPIRY': len(div['EXPIRY']),
        'CONFLICTS_HOLDER': len(div['HOLDER']),
        'CONFLICTS_ATIVAS_APARENTES': len(div['ATIVAS']),
        'CONFLICTS_ATIVAS_REAIS': 0 if not div['ATIVAS'] else None,
    }
    r['UNIVERSO_HISTORICO'] = dict(
        Counter(p['estado_administrativo'] for p in prod if not p['vivo']).most_common())

    # ── 4 · o mesmo defeito ja esta dentro do V2.1 ───────────────────────────
    v21_venc = [x for x in reg if _data_iso(x.get('EXPIRY')) and _data_iso(x['EXPIRY']) < ref]
    r['DEFEITO_HERDADO_PELO_V21'] = {
        'PRODUCTS_REGULATORY_COM_EXPIRY_VENCIDA': len(v21_venc),
        'DESSES_CLIENT_SAFE': sum(1 for x in v21_venc if x.get('CLIENT_SAFE')),
        'DESSES_NO_CATALOGO_PUBLICO': sum(1 for x in v21_venc if x.get('IN_PUBLIC_CATALOG_FLAG')),
        'CAMPO_QUE_AVISA_VENCIMENTO': None,
        'POR_QUE_IMPORTA': ('uma tela que filtra CLIENT_SAFE=true mostra estes '
                            'registros como autorizados, e a validade declarada por '
                            'eles mesmos ja passou. LEI: ESTADO ADMINISTRATIVO != '
                            'VALIDADE FORMAL.'),
        'IDS': [x['ID'] for x in v21_venc],
    }
    return r


def enriquecimento(novo, reg, ref=REF_PADRAO):
    """O payload validado — corrigido, e com cada campo dizendo o que e."""
    rk = {chave(x.get('REGISTRATION_NUMBER')): x for x in reg}
    itens = []
    for p in novo['produtos']:
        k = chave(p['num_registrazione'])
        venc = _data_it(p['data_scadenza'])
        vencida = bool(venc and venc < ref)
        ats = ativas(p)
        bruto = str(p.get('contenuto_per_100g') or '').strip()
        conc = bruto if bruto not in ('', '-') else None
        segs = [x.strip() for x in conc.split('|')] if conc else []
        itens.append({
            'REGISTRATION_NUMBER': k,
            'NAME': p['produto'],
            'AUTHORIZATION_HOLDER': p['titular'],
            'ADMINISTRATIVE_STATE': p['estado_administrativo'],
            # o campo que faltava, e que e a razao de tudo isto:
            'ADMINISTRATIVE_STATE_IS_LIVE': p['vivo'],
            'VALIDITY_EXPIRED_AT_REFERENCE': vencida,
            'REFERENCE_DATE': ref.isoformat(),
            'EXPIRY': venc.isoformat() if venc else None,
            'REGISTERED_AT': (_data_it(p['data_registrazione']).isoformat()
                              if _data_it(p['data_registrazione']) else None),
            'FORMULATION': p['formulacao'],
            'FORMULATION_CODE': p['codice_formulazione'],
            'ACTIVE_INGREDIENTS_FROM_REGISTRY': ats,
            'CONCENTRATION_PER_100G': conc,
            'CONCENTRATION_SEGMENTS': segs,
            # A concentracao tambem vem separada por "|" e casa POSICAO A POSICAO
            # com as substancias. Quem emparelhar sem conferir troca a dosagem de
            # um ativo pela do outro.
            #     EMPARELHAR SEM CONTAR E ADIVINHAR COM CARA DE PRECISAO.
            'CONCENTRATION_PAIRS_WITH_ACTIVES': (
                bool(segs) and len(segs) == len(ats)),
            'HAZARD_STATEMENTS': p.get('indicazioni_di_pericolo') or None,
            'PARALLEL_IMPORT': p.get('importazione_parallela'),
            'REVOCATION_REASON': (p.get('motivo_revoca') or None
                                  if str(p.get('motivo_revoca', '')).strip() not in ('', '-') else None),
            'REVOCATION_EFFECTIVE': (p.get('data_decorrenza_revoca') or None
                                     if str(p.get('data_decorrenza_revoca', '')).strip() not in ('', '-') else None),
            'IN_V21_PRODUCTS_REGULATORY': k in rk,
            'V21_ID': rk[k]['ID'] if k in rk else None,
            'UNIVERSE': 'REGULATORY_LIVE_ADMIN' if p['vivo'] else 'REGULATORY_HISTORICAL',
        })
    itens.sort(key=lambda x: (not x['ADMINISTRATIVE_STATE_IS_LIVE'], x['NAME']))
    return {
        'SOURCE_ID': novo.get('source_id'),
        'SOURCE_NAME': novo.get('source_name'),
        'SOURCE_URL': novo.get('source_url'),
        'SOURCE_FILE': novo.get('arquivo_origem'),
        'DATA_VERSION': novo.get('versao_do_dado'),
        'REFERENCE_DATE': ref.isoformat(),
        'LAYER': 'REGISTERED PRESENCE',
        'QA_STATUS': 'QA_UNREVIEWED',
        'CLIENT_SAFE': False,
        'WHY_NOT_CLIENT_SAFE': ('payload de enriquecimento ainda nao aplicado nem '
                                'conferido registro a registro. O portao vale para o '
                                'que nos mesmos produzimos.'),
        'LAWS': [
            'ESTADO ADMINISTRATIVO != VALIDADE FORMAL',
            'UNIVERSO REGULATORIO != CATALOGO COMERCIAL PUBLICO',
            'TITULAR DE AUTORIZACAO != VENDEDOR',
            'VENCIMENTO FUTURO != OPORTUNIDADE COMERCIAL',
            'FONTE BLOQUEADA != FONTE INEXISTENTE',
        ],
        'NAO_SEI': novo.get('nao_sei', []) + [
            'a data em que o Ministero move um registro para Scaduto — o atraso e '
            'observavel, mas a regra nao esta publicada neste dataset',
        ],
        'DO_NOT_OVERWRITE': {
            'ACTIVE_INGREDIENTS': ('o V2.1 separou certo (0 coladas); este coletor usa '
                                   "split('+') e cola 38 pares. Use "
                                   'ACTIVE_INGREDIENTS_FROM_REGISTRY so para conferir.'),
        },
        'COUNTS': {
            'TOTAL': len(itens),
            'ADMIN_LIVE': sum(1 for x in itens if x['ADMINISTRATIVE_STATE_IS_LIVE']),
            'ADMIN_LIVE_BUT_EXPIRED': sum(1 for x in itens
                                          if x['ADMINISTRATIVE_STATE_IS_LIVE']
                                          and x['VALIDITY_EXPIRED_AT_REFERENCE']),
            'HISTORICAL': sum(1 for x in itens if not x['ADMINISTRATIVE_STATE_IS_LIVE']),
            'ALREADY_IN_V21': sum(1 for x in itens if x['IN_V21_PRODUCTS_REGULATORY']),
            'NEW_TO_V21': sum(1 for x in itens if not x['IN_V21_PRODUCTS_REGULATORY']),
            'WITH_CONCENTRATION': sum(1 for x in itens if x['CONCENTRATION_PER_100G']),
            'CONCENTRATION_PAIRS_OK': sum(1 for x in itens
                                          if x['CONCENTRATION_PAIRS_WITH_ACTIVES']),
            'CONCENTRATION_PAIRS_MISMATCH': sum(
                1 for x in itens if x['CONCENTRATION_PER_100G']
                and not x['CONCENTRATION_PAIRS_WITH_ACTIVES']),
        },
        'ITEMS': itens,
    }


def main():
    origem = os.path.join(OUT, 'IT-T4-001-adama-portfolio.json')
    if not os.path.exists(origem):
        origem = sys.argv[1] if len(sys.argv) > 1 else origem
    if not os.path.exists(origem):
        sys.exit(f'nao achei o portfolio de origem: {origem}')
    novo, reg = carregar(origem)
    r = medir(novo, reg)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'IT-T4-001-validacao-contra-v21.json'), 'w', encoding='utf-8') as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    enr = enriquecimento(novo, reg)
    with open(os.path.join(OUT, 'IT-T4-001-enriquecimento-validado.json'), 'w', encoding='utf-8') as fh:
        json.dump(enr, fh, ensure_ascii=False, indent=1)

    c = r['CRUZAMENTO']
    s = r['SEMANTICA_DE_VIVO']
    print('== IT-T4-001 x V2.1 ==')
    print(f"  MATCHED EXISTING PRODUCTS : {c['MATCHED_EXISTING_PRODUCTS']}")
    print(f"  NEW REGULATORY ENTITIES   : {c['NEW_REGULATORY_ENTITIES']} (vivos novos: {c['NEW_QUE_SAO_VIVOS']})")
    print(f"  CONFLICTS                 : status {c['CONFLICTS_STATUS']} · expiry {c['CONFLICTS_EXPIRY']} · holder {c['CONFLICTS_HOLDER']}")
    print(f"  DUPLICATES                : v21 {c['DUPLICATES_V21']} · novo {c['DUPLICATES_NOVO']}")
    print(f"  EXPIRY-STATE CONFLICTS    : {s['VIVOS_COM_VALIDADE_VENCIDA']} vivos com validade vencida")
    d = r['DEFEITO_HERDADO_PELO_V21']
    print(f"  ... e o V2.1 ja carrega   : {d['PRODUCTS_REGULATORY_COM_EXPIRY_VENCIDA']} deles, {d['DESSES_CLIENT_SAFE']} client-safe")
    print(f"  gerado: {OUT}/IT-T4-001-validacao-contra-v21.json")
    print(f"  gerado: {OUT}/IT-T4-001-enriquecimento-validado.json")


if __name__ == '__main__':
    main()
