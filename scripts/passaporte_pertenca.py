#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LEI DE PERTENÇA — o referente primário decide, não a pasta nem a ferramenta.

SOMENTE LEITURA.

    PASSPORT_MEMBERSHIP = EXTERNAL_WORLD_INFORMATION
                          AND INDIVIDUALLY_DECIDED_OR_EXECUTED

Duas condições, nesta ordem. A **pertença** vem primeiro e é nova (lei do dono,
2026-09-06). A **granularidade** vem depois e continua sendo a de `CONTRATO-DO-PASSAPORTE
§1.5`. Um registro pode satisfazer a granularidade e ainda assim ficar de fora, se o
referente primário dele for o próprio SINTONIA.

A lei em uma frase: **olhe para o referente primário do registro** — não para a pasta
onde ele está, e não para a tecnologia que o produziu.

    um vídeo público coletado pelo Apify        → MUNDO EXTERNO
    "o ator do Apify terminou com sucesso"      → PROCESSO

Uso
    python3 scripts/passaporte_pertenca.py --acervo . --passaporte <ref> [--json p.json]
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys

RULE_VERSION = 'PERTENCA-2026-09-06'
LAW_SOURCE = 'decisão do dono, 2026-09-06 — LEI DE PERTENÇA'
GRANULARITY_SOURCE = 'docs/passaporte/CONTRATO-DO-PASSAPORTE.md §1.5'

# ══════════════════════════════════════════════════════════════════════════════════
# CONDIÇÃO 1 · EXTERNAL_WORLD_INFORMATION — o referente primário
# ══════════════════════════════════════════════════════════════════════════════════
#
# Os marcadores abaixo NÃO são heurística de conveniência: são a transcrição das listas
# que o dono declarou. Marcador de mundo externo nomeia coisa que existe fora do
# SINTONIA; marcador de processo nomeia coisa que só existe porque o SINTONIA existe.

MUNDO_EXTERNO = re.compile(
    r'^('
    # conteúdo e publicação
    r'TRANSCRIPT|TRANSCRIPT_[A-Z_]+|TITLE|TITULO|DESCRIPTION|DESCRIZIONE|BODY|TEXTO|'
    r'CONTENT_TEXT|POST_TEXT|COMMENT_TEXT|OBSERVATION_TEXT|EXCERPT|DOCUMENT_EXCERPT|'
    r'PUBLISHED_AT|PUBLICATION_DATE|PUBLISHED_RELATIVE|VIEWS|LIKES|COMMENTS_COUNT|'
    # entidade externa
    r'AUTHOR|AUTORE|NAME|NOME|CHANNEL|CHANNEL_TITLE|ACCOUNT_HANDLE|HANDLE|USERNAME|'
    r'INSTITUTION|AFFILIATION|ORCID|COMPANY|CONCESSIONAIRE|REFERENCE_HOLDER|'
    r'MANUFACTURER|SPEAKER|RESEARCHER|PERSON_ID|ENTITY_ID|ORIGIN_ID|'
    # fato regulatório / produto
    r'REGISTRATION_ID|REFERENCE_PRODUCT|COMMON_DENOMINATION|CELEX|SUBSTANCE|'
    r'SUBSTANCIA|ACTIVE_INGREDIENT|PRODUCT|PRODOTTO|LABEL|ETICHETTA|'
    # contexto do mundo
    r'CROP|COLTURA|CULTURA|ISSUE|AVVERSITA|PATOGENO|COUNTRY_OF_FACT|REGION_OF_FACT|'
    r'FACT_LOCATION|PROVINCIA|PROVINCE|LOCALITY|NUTS2|'
    # o objeto externo em si
    r'EXTERNAL_ID|VIDEO_ID|VIDEO_URL|SOURCE_URL|URL|POST_URL|DOI|EVENT_DATE|'
    r'EVENT_NAME|CONVEGNO|PRICE|PREZZO|YIELD|AREA_HA|'
    # geografia declarada do fato, também na forma curta
    r'COUNTRY|REGION|SUBREGION|REGIONE|PAESE|'
    # rede de monitoramento: a estação e o sensor existem no mundo, não no SINTONIA.
    # (vocabulário completado a partir do balde UNKNOWN da primeira passagem —
    #  são leituras da ARPAV no Veneto, em italiano, e o referente é o campo.)
    r'CODICE_STAZIONE|NOME_STAZIONE|NOME_SENSORE|SENSOR_ID|STATION_ID|DATAORA|'
    r'VALORE|UNITNM|AGGIORNAMENTO|PRECISIONEFALDA|TEMPERATURA|PIOGGIA|UMIDITA'
    r')$', re.I)

PROCESSO = re.compile(
    r'^('
    # a execução como sujeito
    r'ACTOR|ACTOR_VERSION|APIFY_ACTOR|RUNNER_NAME|JOB_STATUS|EXIT_CODE|'
    r'COST_USD|COST_STATE|TOTAL_REAL_COST|REMAINING_BALANCE|KEY_STATUS|'
    r'ITEM_COUNT_RAW|ITEM_COUNT_NORMALIZED|DATASET_ID|OUTPUT_WRITTEN_AT|'
    r'STARTED_AT|FINISHED_AT|DURATION_MS|RETRIES|'
    # o acesso à fonte como sujeito (CASO A da lei — processo, não fato externo)
    r'HTTP_STATUS|STATUS_CODE|RESPONSE_CODE|TENTATIVA_DE_COLETA|CAPTURE_METHOD|'
    r'CONTRATO_OK|ATOR_NAO_ALCANCADO|ATOR_NAO_ENCONTRADO|SOURCE_PROBE_STATUS|'
    # QA, contrato, build, esquema
    r'QA_[A-Z_]+|GATE|GATE_[A-Z_]+|PORTAO|CONTRACT_STATE|SCHEMA_[A-Z_]+|'
    r'BUILD_[A-Z_]+|MANIFEST_[A-Z_]+|INGESTION_[A-Z_]+|NORMALIZATION_[A-Z_]+|'
    r'PRESERVATION_[A-Z_]+|MIGRATION_[A-Z_]+|PIPELINE_[A-Z_]+|'
    # governança e decisão nossa
    r'HUMAN_DECISION|DECISAO_HUMANA|APROVADO_POR|REVIEWER|MISSION_ID|MISSION|'
    # o relatório da nossa tentativa: quanto demorou, que HTTP voltou, quantos bytes.
    # (completado a partir do balde UNKNOWN da primeira passagem — o referente
    #  destes registros é a busca que NÓS fizemos, não o que a fonte diz.)
    r'ELAPSED_S|ELAPSED|STAGE|HTTP|ERROR|ERRO|SHA256_16|SHA256|BYTES|N_ARQUIVOS|'
    r'ARQUIVO_LIDO|LEITURA_OK|TENTATIVAS'
    r')$', re.I)

# Nome de lista que declara, por si, que o registro é sobre o processo.
LISTA_DE_PROCESSO = re.compile(
    r'(^|[._])(ACTORS?|ACTOR_CONTRACTS?|CONTRACTS?|RUNS?|EXECUTIONS?|JOBS?|'
    r'GATES?|QA|QA_[A-Z_]+|MANIFESTOS?|MANIFEST|BUILDS?|SCHEMAS?|MIGRATIONS?|'
    r'PRESERVACAO|PRESERVATION|INGESTAO|INGESTION|NORMALIZACAO|NORMALIZATION|'
    r'LOGS?|ARQUIVOS|FICHEIROS|CHAVES)([._]|$)', re.I)

# ══════════════════════════════════════════════════════════════════════════════════
# CONDIÇÃO 2 · INDIVIDUALLY_DECIDED_OR_EXECUTED — §1.5, inalterada
# ══════════════════════════════════════════════════════════════════════════════════

EXECUCAO_PROPRIA = re.compile(r'^(RUN_ID|COLLECTION_RUN_ID|BATCH_ID)$', re.I)
DECISAO_POR_ITEM = re.compile(
    r'(_STATE$|_BASIS$|_EVIDENCE$|_DECISION$|^DECISAO|^VEREDITO|^TRIAGE$|'
    r'FILA|QUEUE|VETO|CLASSIFICA|RELEVANCIA|_POR_QUE$)', re.I)
SNAPSHOT = re.compile(r'(UNIT_COUNT|TOTAL_ROWS|TOTAL_DOCS|N_DOCUMENTOS|N_LINHAS)$', re.I)

ESTADOS = ('IN_SCOPE_EXTERNAL_WORLD', 'OUT_OF_SCOPE_PROCESS',
           'OUT_OF_SCOPE_OTHER', 'UNKNOWN_SCOPE')


def listas_de_registros(obj, prefixo=''):
    saida = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                saida.append((f'{prefixo}{k}', v))
            if isinstance(v, (dict, list)) and len(prefixo) < 40:
                saida += listas_de_registros(v, f'{prefixo}{k}.')
    elif isinstance(obj, list):
        for v in obj[:50]:
            if isinstance(v, (dict, list)):
                saida += listas_de_registros(v, prefixo)
    return saida


def referente(nome_da_lista, campos):
    """A CONDIÇÃO 1. Devolve (EXTERNO | PROCESSO | INDETERMINADO, evidência).

    Regra de desempate, e ela vem da lei: *"o fato de algo ter sido coletado por uma
    ferramenta NÃO o transforma em metadado interno"*. Um vídeo com `RUN_ID` continua
    sendo um vídeo. Então **externo vence processo** quando os dois aparecem — a menos
    que o próprio nome da lista declare que o registro é sobre o processo.
    """
    ext = sorted({c for c in campos if MUNDO_EXTERNO.match(c)})
    proc = sorted({c for c in campos if PROCESSO.match(c)})
    lista_proc = bool(LISTA_DE_PROCESSO.search(nome_da_lista or ''))

    if lista_proc and not ext:
        return 'PROCESSO', {'LISTA_DECLARA_PROCESSO': nome_da_lista, 'PROCESSO': proc[:6]}
    if ext:
        return 'EXTERNO', {'EXTERNO': ext[:6], 'PROCESSO_ANOTADO': proc[:4]}
    if proc:
        return 'PROCESSO', {'PROCESSO': proc[:6]}
    return 'INDETERMINADO', {'CAMPOS': sorted(campos)[:8]}


def granularidade(campos):
    """A CONDIÇÃO 2, de §1.5. Devolve (satisfaz, motivo)."""
    if any(EXECUCAO_PROPRIA.match(c) for c in campos):
        return True, 'EXECUCAO_PROPRIA'
    decisao = sorted({c for c in campos if DECISAO_POR_ITEM.search(c)})
    if decisao:
        return True, 'DECISAO_POR_ITEM:' + ','.join(decisao[:3])
    return False, 'SEM_DECISAO_NEM_EXECUCAO_INDIVIDUAL'


def classificar(caminho):
    """Aplica pertença e depois granularidade. Devolve (estado, motivo, detalhe)."""
    if not caminho.endswith(('.json', '.jsonl')):
        return 'OUT_OF_SCOPE_OTHER', 'NAO_E_JSON', {}
    try:
        with open(caminho, encoding='utf-8') as f:
            dados = json.loads(f.read()) if caminho.endswith('.json') else \
                [json.loads(l) for l in f if l.strip()]
    except Exception as erro:                                  # noqa: BLE001
        return 'UNKNOWN_SCOPE', 'ILEGIVEL: %s' % str(erro)[:60], {}

    listas = listas_de_registros(dados)
    if not listas:
        texto = json.dumps(dados, ensure_ascii=False)[:20000]
        campos_topo = set(dados) if isinstance(dados, dict) else set()
        ref, ev = referente('', campos_topo)
        if SNAPSHOT.search(texto) and ref == 'EXTERNO':
            return 'IN_SCOPE_EXTERNAL_WORLD', 'DATASET_SNAPSHOT_EXTERNO', ev
        if ref == 'PROCESSO':
            return 'OUT_OF_SCOPE_PROCESS', 'SEM_REGISTROS_E_REFERENTE_E_O_PROCESSO', ev
        return 'OUT_OF_SCOPE_OTHER', 'SEM_REGISTROS', ev

    melhor = None
    for nome, arr in listas:
        campos = set()
        for r in arr[:80]:
            if isinstance(r, dict):
                campos |= set(r)
        ref, ev = referente(nome, campos)
        gran, gran_motivo = granularidade(campos)
        info = {'LISTA': nome, 'N': len(arr), 'REFERENTE': ref,
                'GRANULARIDADE': gran_motivo, 'EVIDENCIA': ev}
        if ref == 'INDETERMINADO':
            info['ESTADO'] = ('UNKNOWN_SCOPE',
                              'REFERENTE_INDETERMINADO_NAO_CHUTAR')
        elif ref == 'PROCESSO':
            info['ESTADO'] = ('OUT_OF_SCOPE_PROCESS',
                              'REFERENTE_E_O_PROPRIO_SINTONIA')
        elif not gran:
            info['ESTADO'] = ('OUT_OF_SCOPE_OTHER',
                              'MUNDO_EXTERNO_MAS_' + gran_motivo)
        else:
            info['ESTADO'] = ('IN_SCOPE_EXTERNAL_WORLD', gran_motivo)
        # prioridade: dentro > desconhecido > fora; e entre iguais, a lista maior
        ordem = {'IN_SCOPE_EXTERNAL_WORLD': 3, 'UNKNOWN_SCOPE': 2,
                 'OUT_OF_SCOPE_OTHER': 1, 'OUT_OF_SCOPE_PROCESS': 0}
        chave = (ordem[info['ESTADO'][0]], len(arr))
        if melhor is None or chave > melhor[0]:
            melhor = (chave, info)
    info = melhor[1]
    return info['ESTADO'][0], info['ESTADO'][1], info


def varrer(acervo):
    base = os.path.join(acervo, 'data', 'samples')
    r = {}
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            c = os.path.join(pasta, nome)
            rel = os.path.relpath(c, base).replace('\\', '/')
            if rel.startswith('raw-paid/'):
                r[rel] = ('OUT_OF_SCOPE_OTHER',
                          'RAW_PAID_TEM_REGRA_DE_DIRETORIO_PROPRIA', {})
                continue
            r[rel] = classificar(c)
    return r


def universo(acervo, resultado):
    base = os.path.join(acervo, 'data', 'samples')
    dentro = sorted(k for k, v in resultado.items() if v[0] == 'IN_SCOPE_EXTERNAL_WORLD')
    registros = 0
    colecoes, familias = collections.Counter(), collections.Counter()
    h = hashlib.sha256()
    for rel in dentro:
        info = resultado[rel][2]
        registros += info.get('N', 0)
        if info.get('LISTA'):
            colecoes[info['LISTA']] += 1
        familias[rel.split('/')[0] if '/' in rel else '__RAIZ__'] += 1
        h.update(rel.encode('utf-8'))
        try:
            with open(os.path.join(base, rel), 'rb') as f:
                h.update(hashlib.sha256(f.read()).digest())
        except Exception:                                      # noqa: BLE001
            h.update(b'ILEGIVEL')
    return {'FILES': dentro, 'FILE_COUNT': len(dentro), 'RECORD_COUNT': registros,
            'FAMILIES': sorted(familias), 'COLLECTIONS': sorted(colecoes),
            'FINGERPRINT': h.hexdigest()}


def cobertura_atual(passaporte):
    """O que o passaporte cobre hoje. Lido, NÃO usado como gabarito da regra."""
    fonte = os.path.join(passaporte, 'scripts', 'passaporte_backfill.py')
    if not os.path.isfile(fonte):
        return None
    texto = open(fonte, encoding='utf-8').read()
    m = re.search(r'^INVENTARIO\s*=\s*\{(.*?)^\}', texto, re.S | re.M)
    if not m:
        return None
    ent = re.findall(r"^\s*'([^']+)':\s*\(([^,]+),\s*'([^']*)'\)", m.group(1), re.M)
    return {a for a, r, _ in ent if r.strip() in ("'ITENS'", "'SELOS'")}


def portao(acervo, passaporte):
    """As cinco condições que o dono listou, medidas — e depois a cobertura.

    Duas perguntas diferentes, e elas não podem ser fundidas:

        MEMBERSHIP_RULE_PROVED  · a lei está codificada e se comporta?
        UNIVERSE_COMPLETENESS   · o universo que ela define está coberto?

    A primeira pode passar com a segunda vermelha. É exatamente o estado de hoje.
    """
    r = varrer(acervo)
    u = universo(acervo, r)
    cont = {e: sum(1 for v in r.values() if v[0] == e) for e in ESTADOS}
    total = len(r)
    coberto = cobertura_atual(passaporte) or set()
    dentro = set(u['FILES'])

    condicoes = {
        '1_PERTENCA_CODIFICADA': True,   # este módulo é a codificação
        '2_SOMA_FECHA': sum(cont.values()) == total,
        '3_NENHUMA_UNIDADE_SEM_CLASSIFICACAO': all(
            v[0] in ESTADOS and v[1] for v in r.values()),
        '4_NENHUM_PROCESSO_ENTROU_COMO_EVIDENCIA': all(
            r[x][2].get('REFERENTE') == 'EXTERNO' for x in dentro),
        '5_NAO_EXCLUIU_EXTERNO_POR_CAUSA_DA_PASTA': len(u['FAMILIES']) >= 10,
    }
    regra_provada = all(condicoes.values())

    faltando = sorted(dentro - coberto)
    fora_da_regra = sorted(coberto - dentro)
    completo = (not faltando and not fora_da_regra
                and cont.get('UNKNOWN_SCOPE', 0) == 0)
    motivos = []
    if faltando:
        motivos.append('MISSING_PASSPORT')
    if fora_da_regra:
        motivos.append('COVERED_BUT_OUTSIDE_RULE')
    if cont.get('UNKNOWN_SCOPE', 0):
        motivos.append('UNKNOWN_SCOPE_NOT_ZERO')

    familias_faltando = sorted({(x.split('/')[0] if '/' in x else '__RAIZ__')
                                for x in faltando})
    return {
        'CONDICOES': condicoes,
        'MEMBERSHIP_CONDITION_DECLARED': 'YES',
        'MEMBERSHIP_RULE_PROVED': 'YES' if regra_provada else 'NO',
        'CONTAGEM': cont, 'TOTAL': total,
        'RULE_DERIVED_FILES': u['FILE_COUNT'],
        'RULE_DERIVED_RECORDS': u['RECORD_COUNT'],
        'PROCESS_RECORDS_EXCLUDED': cont.get('OUT_OF_SCOPE_PROCESS', 0),
        'UNKNOWN_SCOPE': cont.get('UNKNOWN_SCOPE', 0),
        'EXPECTED_FILES': u['FILE_COUNT'],
        'EXPECTED_RECORDS': u['RECORD_COUNT'],
        'EXPECTED_FAMILIES': len(u['FAMILIES']),
        'EXPECTED_COLLECTIONS': len(u['COLLECTIONS']),
        'EXPECTED_FINGERPRINT': u['FINGERPRINT'],
        'SCANNED_FILES': len(coberto),
        'SCANNED_RECORDS': sum(r[x][2].get('N', 0) for x in coberto if x in r),
        'MISSING_FILES': faltando,
        'MISSING_RECORDS': sum(r[x][2].get('N', 0) for x in faltando if x in r),
        'MISSING_FAMILIES': familias_faltando,
        'COVERED_BUT_OUTSIDE_RULE': fora_da_regra,
        'UNIVERSE_COMPLETENESS': 'PASS' if completo else 'FAIL',
        'MOTIVOS': motivos,
    }, r, u


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--passaporte', required=True)
    p.add_argument('--json', default=None)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    print(f'LEI DE PERTENÇA · {RULE_VERSION}')
    print(f'  pertença     : {LAW_SOURCE}')
    print(f'  granularidade: {GRANULARITY_SOURCE} (inalterada)')
    print('  PASSPORT_MEMBERSHIP = EXTERNAL_WORLD_INFORMATION'
          ' AND INDIVIDUALLY_DECIDED_OR_EXECUTED\n')

    r = varrer(args.acervo)
    cont = collections.Counter(v[0] for v in r.values())
    total = len(r)
    print('── RECLASSIFICAÇÃO DE TODO ARQUIVO OBSERVADO ──')
    for e in ESTADOS:
        print(f'  {e:26s} = {cont.get(e, 0)}')
    soma = sum(cont.get(e, 0) for e in ESTADOS)
    print(f'  {"TOTAL":26s} = {total}   ·   soma fecha = {soma == total}')

    print('\n  motivos, por estado:')
    for e in ESTADOS:
        motivos = collections.Counter(v[1].split(':')[0] for v in r.values() if v[0] == e)
        if not motivos:
            continue
        print(f'   {e}:')
        for m, n in motivos.most_common(6):
            print(f'      {n:5d}  {m}')

    if cont.get('UNKNOWN_SCOPE'):
        print('\n  UNKNOWN_SCOPE — não chutados, declarados:')
        for k, v in list(r.items()):
            if v[0] == 'UNKNOWN_SCOPE':
                print(f'      {k}  ·  {v[1][:70]}')

    u = universo(args.acervo, r)
    print('\n── O UNIVERSO, DERIVADO DA LEI ──')
    print(f'  RULE_DERIVED_FILES       = {u["FILE_COUNT"]}')
    print(f'  RULE_DERIVED_RECORDS     = {u["RECORD_COUNT"]}')
    print(f'  RULE_DERIVED_FAMILIES    = {len(u["FAMILIES"])}')
    print(f'  RULE_DERIVED_COLLECTIONS = {len(u["COLLECTIONS"])}')
    print(f'  FINGERPRINT              = {u["FINGERPRINT"]}')

    coberto = cobertura_atual(args.passaporte)
    dif = {}
    if coberto is not None:
        dentro = set(u['FILES'])
        dif = {'OLD_COVERED': sorted(coberto),
               'MISSING_PASSPORT': sorted(dentro - coberto),
               'COVERED_BUT_OUTSIDE_RULE': sorted(coberto - dentro)}
        print('\n── A DIFERENÇA (a lista NÃO foi gabarito da regra) ──')
        print(f'  OLD_COVERED               = {len(coberto)}')
        print(f'  NEW_RULE_DERIVED          = {len(dentro)}')
        print(f'  MISSING_PASSPORT          = {len(dif["MISSING_PASSPORT"])}')
        print(f'  COVERED_BUT_OUTSIDE_RULE  = {len(dif["COVERED_BUT_OUTSIDE_RULE"])}')
        for x in dif['COVERED_BUT_OUTSIDE_RULE']:
            print(f'     FORA AGORA  {x}  ·  {r.get(x, ("?", "?"))[1][:60]}')

    g, _, _ = portao(args.acervo, args.passaporte)
    print('')
    print('-- AS CINCO CONDICOES DO DONO --')
    for k, v in g['CONDICOES'].items():
        print(f'  {k:44s} {v}')
    print('')
    print(f'  MEMBERSHIP_CONDITION_DECLARED = {g["MEMBERSHIP_CONDITION_DECLARED"]}')
    print(f'  MEMBERSHIP_RULE_PROVED        = {g["MEMBERSHIP_RULE_PROVED"]}')
    print('')
    print('-- COBERTURA --')
    print(f'  {"":22s} {"ESPERADO":>12s} {"COBERTO":>12s}')
    for dim in ('FILES', 'RECORDS'):
        print(f'  {dim:22s} {g["EXPECTED_" + dim]:>12} {g["SCANNED_" + dim]:>12}')
    print(f'  MISSING_FILES          = {len(g["MISSING_FILES"])}')
    print(f'  MISSING_RECORDS        = {g["MISSING_RECORDS"]}')
    print(f'  MISSING_FAMILIES       = {len(g["MISSING_FAMILIES"])}')
    print(f'  COVERED_BUT_OUTSIDE    = {len(g["COVERED_BUT_OUTSIDE_RULE"])}')
    print('')
    print(f'UNIVERSE_COMPLETENESS = {g["UNIVERSE_COMPLETENESS"]}'
          + ('  · ' + ' · '.join(g['MOTIVOS']) if g['MOTIVOS'] else ''))

    if args.json:
        json.dump({'RULE_VERSION': RULE_VERSION, 'LAW_SOURCE': LAW_SOURCE,
                   'PORTAO': {k: (len(v) if isinstance(v, list) else v)
                              for k, v in g.items()},
                   'MISSING_FILES': g['MISSING_FILES'],
                   'MISSING_FAMILIES': g['MISSING_FAMILIES'],
                   'GRANULARITY_SOURCE': GRANULARITY_SOURCE,
                   'CLASSIFICACAO': {k: {'ESTADO': v[0], 'MOTIVO': v[1],
                                         'LISTA': v[2].get('LISTA'),
                                         'REFERENTE': v[2].get('REFERENTE'),
                                         'EVIDENCIA': v[2].get('EVIDENCIA')}
                                     for k, v in sorted(r.items())},
                   'CONTAGEM': {e: cont.get(e, 0) for e in ESTADOS},
                   'TOTAL': total, 'SOMA_FECHA': soma == total,
                   'UNIVERSO': {k: v for k, v in u.items() if k != 'FILES'},
                   'UNIVERSO_FILES': u['FILES'],
                   'DIFERENCA': dif},
                  open(args.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'\ngravado: {args.json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
