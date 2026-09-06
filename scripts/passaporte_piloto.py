#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PILOTO DE ETIQUETAGEM — amostra estratificada, SOMENTE LEITURA.

Não é backfill. Não escreve passaporte, não escreve evento, não altera o acervo.
Ele responde uma pergunta só:

    quantos campos do passaporte universal conseguem ser preenchidos HOJE
    a partir de prova que já existe no acervo — e quantos ficam UNKNOWN?

Regra dura: um campo só é preenchido se houver valor E o valor não for sentinela.
Sentinela com sufixo explicativo (`"NÃO SEI — a rota …"`) conta como AUSENTE — foi
exatamente essa a armadilha que produziu 346 estados falsos no PASSPORT-1.0.

Uso:  python3 scripts/passaporte_piloto.py [--n POR_FAMILIA] [--json SAIDA]
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

# ── sentinelas: exata E com sufixo ────────────────────────────────────────────────
_EXATA = {'NÃO SEI', 'NAO SEI', 'NOT_KNOWN', 'NAO_DECLARADO', 'NOT_DECLARED',
          'UNKNOWN', 'NULL', 'NONE', 'N/A', ''}
_SUFIXO = re.compile(r'^\s*(NÃO SEI|NAO SEI|NOT_KNOWN|UNKNOWN)\s*[—\-–:·]', re.IGNORECASE)


def sabido(v):
    """A trava corrigida: pega a sentinela exata E a sentinela com explicação."""
    if v is None:
        return False
    if isinstance(v, (list, dict)):
        return len(v) > 0
    s = str(v).strip()
    if s.upper() in _EXATA:
        return False
    return not _SUFIXO.match(s)


# ── amostra estratificada ─────────────────────────────────────────────────────────
# Uma família por natureza de evidência, escolhidas para NÃO serem só as fáceis.
# IT-ROTULOS* está fora de propósito: é Label Intelligence, fora do escopo da missão.
FAMILIAS = [
    ('science',              'IT-CIENCIA'),
    ('competitor',           'COMPETITOR-PUBLIC-COMM'),
    ('creator_public_voice', 'CREATOR-MAP-EAME'),
    ('market',               'IT-MERCADO'),
    ('climate',              'IT-ARPAV-VENETO'),
    ('phytosanitary',        'IT-CAMPO-V1'),
    ('news_event',           'IT-FUTURO-V1'),
    ('regulatory',           'IT-T4-001'),
    ('territorial',          'TERRITORIAL'),
    ('field_sensor',         'SENSOR-PILOT'),
]

# ── os eixos do passaporte universal, e onde procurar cada um no acervo ───────────
# A lista de nomes é o MAPA (PASSPORT-FIELD-MAPPING.json) aplicado: procura-se pelo
# nome do dono canônico primeiro, e só depois pelos nomes herdados.
EIXOS = {
    'ITEM_ID':            ['ITEM_ID', 'CONTENT_ID', 'ID'],
    'EXTERNAL_ID':        ['EXTERNAL_ID', 'REGISTRATION_ID', 'ORCID', 'DOI'],
    'SOURCE_ID':          ['SOURCE_ID'],
    'SOURCE_FAMILY':      ['SOURCE_FAMILY'],
    'COLLECTION_ID':      ['COLLECTION_ID', 'COLLECTION_RUN_ID', 'RUN_ID'],
    'CONTENT_STATE':      ['TRANSCRIPT_AVAILABLE', 'CONTENT_STATE', 'RAW_STATE'],
    'READ_SCOPE':         ['READ_SCOPE'],
    'CLAIM_TYPE':         ['CLAIM_TYPE', 'CHANGE_TYPE', 'TIPO_DE_FATO', 'CONTENT_TYPE'],
    'OBSERVATION_STATE':  ['OBSERVATION_STATE'],
    'PROOF_STATE':        ['PROOF_STATE'],
    'EVIDENCE_CLASS':     ['EVIDENCE_CLASS'],
    'IDENTITY_STATE':     ['IDENTITY_STATE', 'CHANNEL_IDENTITY_STATE', 'ORIGIN_STATUS'],
    'ENTITY_ID':          ['ENTITY_ID', 'PERSON_ID', 'REFERENCE_HOLDER'],
    'COUNTRY_OF_FACT':    ['COUNTRY_OF_FACT'],
    'REGION_OF_FACT':     ['REGION_OF_FACT', 'FACT_REGION'],
    'SUBREGION':          ['SUBREGION', 'provincia', 'PROVINCIA'],
    'FACT_LOCATION':      ['FACT_LOCATION'],
    'SOURCE_LOCATION':    ['SOURCE_LOCATION'],
    'ENTITY_LOCATION':    ['COUNTRY_OF_PERSON', 'ENTITY_LOCATION'],
    'CROP':               ['CROP', 'CROP_ALL', 'crop', 'CULTURA'],
    'CROP_CARDINALITY':   ['CROP_CARDINALITY'],
    'ISSUE':              ['ISSUE', 'ISSUE_ID', 'ALVO'],
    'ISSUE_TYPE':         ['ISSUE_TYPE'],
    'PUBLISHED_AT':       ['PUBLISHED_AT', 'PUBLICATION_DATE', 'DATE'],
    'OBSERVED_AT':        ['OBSERVED_AT', 'DATA_DO_FATO', 'FACT_DATE'],
    'CAPTURED_AT':        ['CAPTURED_AT', 'captured_at'],
    'VALID_FROM':         ['VALID_FROM'],
    'VALID_UNTIL':        ['VALID_UNTIL', 'SCADENZA', 'CADUCIDAD'],
    'INDEPENDENCE_STATE': ['ORIGINALITY', 'VIDEO_ORIGINALITY', 'ORIGINALIDADE'],
    'LINEAGE_STATE':      ['PARENT_ITEM_ID', 'DERIVED_FROM'],
    'ADAMA_RELATION':     ['ADAMA_RELATION', 'ADAMA_USE_CASE'],
    'PRODUCT_RELATION':   ['PRODUCT_RELATION', 'productKey'],
    'CAPABILITY_ROUTING': ['CAPABILITY_ID', 'CAPABILITY_ROUTING'],
    'CONSUMPTION_STATE':  ['CONSUMPTION_STATE'],
    'EVIDENCE_POINTER':   ['EVIDENCE_REFERENCE', 'RAW_EVIDENCE_PATH', 'SOURCE_URL', 'URL'],
}


def registros_da_familia(base, pasta, teto):
    """Devolve até `teto` registros da família, e a lista de arquivos que os deu."""
    raiz = os.path.join(base, 'data', 'samples', pasta)
    if not os.path.isdir(raiz):
        return [], [], f'pasta ausente: {pasta}'
    saida, arquivos = [], []
    for pai, _, nomes in os.walk(raiz):
        for nome in sorted(nomes):
            if not nome.endswith('.json'):
                continue
            caminho = os.path.join(pai, nome)
            try:
                with open(caminho, encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception as erro:                          # noqa: BLE001
                arquivos.append((caminho, f'ILEGIVEL: {str(erro)[:50]}'))
                continue
            topo = dados if isinstance(dados, dict) else {}
            lista = None
            if isinstance(dados, list):
                lista = dados
            else:
                for chave, valor in dados.items():
                    if isinstance(valor, list) and valor and isinstance(valor[0], dict):
                        lista = valor
                        break
            if not lista:
                continue
            arquivos.append((caminho, f'{len(lista)} registros'))
            for reg in lista:
                if not isinstance(reg, dict):
                    continue
                # o registro herda o cabeçalho do arquivo: SOURCE_ID, SOURCE_LOCATION,
                # EVIDENCE_CLASS etc. moram no topo, não na linha
                fundido = {k: v for k, v in topo.items() if not isinstance(v, (list, dict))}
                fundido.update(reg)
                fundido['__ARQUIVO__'] = os.path.relpath(caminho, base)
                saida.append(fundido)
                if len(saida) >= teto:
                    return saida, arquivos, None
    return saida, arquivos, None


def medir(registro):
    """Para cada eixo: PREENCHIDO (com o nome que serviu) ou UNKNOWN."""
    resultado = {}
    for eixo, candidatos in EIXOS.items():
        achou = None
        for nome in candidatos:
            if nome in registro and sabido(registro[nome]):
                achou = nome
                break
        resultado[eixo] = achou
    return resultado


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=25, help='registros por família')
    p.add_argument('--base', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    p.add_argument('--json', default=None)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    print('PILOTO DE ETIQUETAGEM — somente leitura, nenhum passaporte escrito')
    print(f'amostra: até {args.n} registros por família · {len(FAMILIAS)} famílias\n')

    total_reg = 0
    por_eixo = collections.Counter()
    por_eixo_nome = collections.defaultdict(collections.Counter)
    por_familia = {}
    familias_vazias = []

    for etiqueta, pasta in FAMILIAS:
        regs, arquivos, erro = registros_da_familia(args.base, pasta, args.n)
        if erro or not regs:
            familias_vazias.append((etiqueta, pasta, erro or 'nenhum registro em lista'))
            continue
        preenchidos = collections.Counter()
        for r in regs:
            m = medir(r)
            for eixo, nome in m.items():
                if nome:
                    preenchidos[eixo] += 1
                    por_eixo[eixo] += 1
                    por_eixo_nome[eixo][nome] += 1
        total_reg += len(regs)
        cobertura = sum(preenchidos.values()) / (len(regs) * len(EIXOS))
        por_familia[etiqueta] = {
            'PASTA': pasta, 'REGISTROS': len(regs),
            'COBERTURA': round(cobertura, 3),
            'EIXOS_PREENCHIDOS': len([e for e in preenchidos if preenchidos[e] > 0]),
        }
        print(f'  {etiqueta:22s} {pasta:26s} {len(regs):4d} reg · '
              f'{len([e for e in preenchidos if preenchidos[e]>0]):2d}/{len(EIXOS)} eixos · '
              f'cobertura {cobertura:5.1%}')

    if familias_vazias:
        print('\n  FAMÍLIAS NÃO MEDIDAS (não é zero — é não medido):')
        for etiqueta, pasta, motivo in familias_vazias:
            print(f'     {etiqueta:22s} {pasta:26s} {motivo}')

    print(f'\nITEMS_TESTED = {total_reg}')
    campos_possiveis = total_reg * len(EIXOS)
    preenchidos_total = sum(por_eixo.values())
    print(f'FIELDS_POPULATED_FROM_EXISTING_PROOF = {preenchidos_total} '
          f'({preenchidos_total / campos_possiveis:.1%} de {campos_possiveis})')
    print(f'FIELDS_UNKNOWN = {campos_possiveis - preenchidos_total}')

    print('\n── COBERTURA POR EIXO ──')
    for eixo in EIXOS:
        n = por_eixo[eixo]
        pct = n / total_reg if total_reg else 0
        nomes = ' · '.join(f'{k}({v})' for k, v in por_eixo_nome[eixo].most_common(3))
        marca = '  ← VAZIO' if n == 0 else ''
        print(f'  {eixo:20s} {n:5d}/{total_reg} {pct:6.1%}  {nomes[:60]}{marca}')

    vazios = [e for e in EIXOS if por_eixo[e] == 0]
    print(f'\nEIXOS QUE NENHUM REGISTRO DA AMOSTRA CONSEGUE PREENCHER: {len(vazios)}')
    for e in vazios:
        print(f'   {e}')

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({
                'ITEMS_TESTED': total_reg,
                'FIELDS_POPULATED_FROM_EXISTING_PROOF': preenchidos_total,
                'FIELDS_UNKNOWN': campos_possiveis - preenchidos_total,
                'POR_FAMILIA': por_familia,
                'POR_EIXO': {e: por_eixo[e] for e in EIXOS},
                'EIXOS_VAZIOS': vazios,
                'FAMILIAS_NAO_MEDIDAS': [
                    {'FAMILIA': a, 'PASTA': b, 'MOTIVO': c} for a, b, c in familias_vazias],
            }, f, ensure_ascii=False, indent=2)
        print(f'\ngravado: {args.json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
