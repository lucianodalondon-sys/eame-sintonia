#!/usr/bin/env python3
"""
IMPORTADOR DETERMINÍSTICO — artefato do Git -> linhas normalizadas -> SQL idempotente.

    python3 scripts/catalogo_importar.py --linhas   # normaliza e escreve o JSON de linhas
    python3 scripts/catalogo_importar.py --sql      # escreve o SQL idempotente
    python3 scripts/catalogo_importar.py --aplicar  # exige psql + SUPABASE_DB_URL

Por que gera SQL em vez de falar direto com o banco: o SQL é AUDITÁVEL. Ele entra no Git,
alguém lê antes de rodar, e o mesmo arquivo pode ser aplicado por qualquer via (psql,
workflow, console). Um importador que só existe como processo não deixa rastro do que fez.

AS SEIS EXIGÊNCIAS DA SEÇÃO 20, E ONDE CADA UMA VIVE

    IDEMPOTENT              todo INSERT tem ON CONFLICT DO NOTHING sobre uma chave
                            NATURAL. Rodar duas vezes com a mesma fonte_versao insere 0.
    COUNTRY_AWARE           pais entra na chave da captura, não só na linha.
    SOURCE_VERSION_AWARE    a captura é única por (pais, fabricante, fonte_versao).
                            Fonte nova = captura nova = linhas novas ao lado, não por cima.
    NO_FUZZY_SILENT_MATCH   crop_id/issue_id só são preenchidos por casamento EXATO do
                            rótulo oficial contra a tabela de ids do MAPA. Sem casar,
                            fica NULL e o rótulo publicado permanece. Nunca aproxima.
    NO_CARTESIAN            só entram em cultivo_agente os pares que já vêm com âncora de
                            linha no artefato. O schema recusa o resto de qualquer forma.
    NO_OVERWRITE_HISTORY    nenhum UPDATE, nenhum DELETE, nenhum UPSERT que sobrescreva.
                            Só INSERT ... DO NOTHING.
"""
import json
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')

ARTEFATO = os.path.join(SAMPLES, 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')
CONFIRMACAO = os.path.join(SAMPLES, 'ADAMA-ES-CONFIRMACAO-REGULATORIA-DO-PAR.json')
IDS_MAPA = os.path.join(SAMPLES, 'ES-MAPA-VOCABULARIO-IDS.json')
PRESERVACAO = os.path.join(SAMPLES, 'ADAMA-ES-PRESERVACAO-RELATORIO.json')
PLANO = os.path.join(SAMPLES, 'ADAMA-ES-PRESERVACAO-PLANO.json')

# As linhas normalizadas vão para data/normalized/, que NÃO é versionado: são 549 KB
# inteiramente deriváveis do artefato por este mesmo script. O que entra no Git é o SQL
# — esse sim é o que alguém vai ler antes de aplicar. Os testes recalculam em vez de ler
# daqui, para não passarem em silêncio numa máquina limpa.
LINHAS_OUT = os.path.join(ROOT, 'data', 'normalized', 'ADAMA-ES-IMPORT-LINHAS.json')
SQL_OUT = os.path.join(ROOT, 'supabase', 'importacoes',
                       'ADAMA-ES-CATALOGO-2026-08-30.sql')

PAIS = 'ES'
FABRICANTE = 'ADAMA'
RULE_VERSION = 'M12-PRESERVACAO-2026-08-30'
MISSION = '12-PRESERVAR-E-INTEGRAR-COLETA-LOCAL-ES'


# ── utilidades ───────────────────────────────────────────────────────────────

def _ler(caminho, obrigatorio=True):
    if not os.path.exists(caminho):
        if obrigatorio:
            raise SystemExit('ausente: %s' % caminho)
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _chave(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in s).split())


def q(v):
    """Literal SQL. None vira NULL de verdade, não a string 'None'."""
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def qj(v):
    return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"


def _nao_sei(v):
    """'NÃO SEI' e '' são AUSÊNCIA. Guardar a string 'NÃO SEI' no banco faria
    `where registration_id is null` mentir."""
    if v in (None, '', 'NÃO SEI', 'NAO SEI', 'NOT_COLLECTED', 'NÃO SEI '):
        return None
    return v


# ── normalização ─────────────────────────────────────────────────────────────

def normalizar():
    art = _ler(ARTEFATO)
    conf = _ler(CONFIRMACAO, obrigatorio=False) or {}
    ids = _ler(IDS_MAPA)
    pres = _ler(PRESERVACAO, obrigatorio=False)
    plano = _ler(PLANO, obrigatorio=False) or {}

    crops_id = {k: v['ID'] for k, v in ids['CROPS'].items()}
    issues_id = {k: v['ID'] for k, v in ids['ISSUES'].items()}

    fonte_versao = art['captured_at']
    run_id = 'ES-M12-IMPORT-CATALOGO-ADAMA-%s-a' % fonte_versao[:10]

    # Asset preservado por objeto — só entra o que foi VERIFICADO de verdade.
    verificados = {}
    for a in ((pres or {}).get('ASSETS') or []):
        if a.get('ESTADO') in ('VERIFIED', 'ALREADY_PRESENT_VERIFIED'):
            verificados[a['SHA256']] = a['OBJETO']

    produtos = [p for p in art['PRODUCTS'] if p.get('PRODUCT_ID')]

    def cid(rotulo):
        return crops_id.get(_chave(rotulo))

    def iid(rotulo):
        return issues_id.get(_chave(rotulo))

    linhas = {
        'RUN': {
            'run_id': run_id, 'platform': 'ADAMA_WEBSITE',
            'actor': 'scripts/adama_es.py + navegador local',
            'mission': MISSION, 'source_country': PAIS,
            'capture_method': ('bytes capturados por NAVEGADOR LOCAL na maquina do '
                               'usuario; curl/urllib recebem 403 da borda Akamai'),
            'source_version': fonte_versao, 'rule_version': RULE_VERSION,
            'item_count_raw': plano.get('ITENS'),
            'item_count_normalized': len(produtos),
        },
        'CAPTURA': {
            'run_id': run_id, 'pais': PAIS, 'fabricante': FABRICANTE,
            'catalogo_url': 'https://www.adama.com/spain/es/nuestras-soluciones?items_per_page=All',
            'capturado_em': fonte_versao,
            'metodo_de_captura': 'NAVEGADOR_LOCAL',
            'fonte_versao': fonte_versao, 'rule_version': RULE_VERSION,
            'total_no_catalogo': art['CENSO']['CURRENT_CATALOG_TOTAL'],
            'enumeracao_completa': art['CENSO']['ENUMERATION_COMPLETE'] == 'YES',
            'e_baseline': True,
        },
        'PRODUTO': [], 'DOCUMENTO': [], 'CULTIVO': [], 'AGENTE': [], 'AMBIGUO': [],
        'PAR': [], 'DOSE': [], 'JANELA': [], 'SUBSTANCIA': [], 'MOA': [],
        'CLAIM': [], 'TECNOLOGIA': [], 'RELACAO': [], 'CROSSWALK': [], 'RAW_ASSET': [],
    }

    for p in produtos:
        linhas['PRODUTO'].append({
            'product_id': p['PRODUCT_ID'], 'pais': PAIS,
            'nome_publicado': p['DISPLAY_NAME'],
            'categoria': p.get('CATEGORY') or 'NAO_SEI',
            'pagina_url': p['PAGE_URL'],
            'registration_id': _nao_sei(p.get('REGISTRATION_ID')),
            'formulacao': _nao_sei(p.get('FORMULATION')),
            'composicao_texto': _nao_sei(p.get('COMPOSITION_TEXT_PUBLICADO')),
        })
        for a in p.get('ACTIVE_INGREDIENTS') or []:
            linhas['SUBSTANCIA'].append({
                'product_id': p['PRODUCT_ID'],
                'texto_publicado': a['NAME'],
                # Normalização ainda NÃO foi feita: nome_normalizado fica NULL de
                # propósito. Copiar o texto publicado para cá fingiria que houve regra.
                'nome_normalizado': None, 'regra_normalizacao': None,
                'concentracao': _nao_sei(a.get('CONCENTRATION')),
                'concentracao_unidade': _nao_sei(a.get('CONCENTRATION_UNIT')),
                'codigo_formulacao': _nao_sei(a.get('FORMULATION_CODE')),
            })

    for d in art['DOCUMENTS']:
        estado = d.get('DOWNLOAD_STATE') or 'NOT_ATTEMPTED'
        sha = _nao_sei(d.get('SHA256'))
        objeto = verificados.get(sha) if sha else None
        linhas['DOCUMENTO'].append({
            'product_id': d['PRODUCT_ID'], 'document_id': d['DOCUMENT_ID'],
            'tipo': d['DOCUMENT_TYPE'], 'tipo_evidencia': d['TYPE_EVIDENCE'],
            'prova_de_que_e_documento': d.get('PROVA_DE_QUE_E_DOCUMENTO') or 'NAO_DECLARADA',
            'url': d['URL'], 'pagina_origem': d['SOURCE_PAGE'],
            'nome_arquivo': _nao_sei(d.get('FILENAME')),
            'data_visivel': _nao_sei(d.get('VISIBLE_DOCUMENT_DATE')),
            'http_status': _nao_sei(d.get('HTTP_STATUS')),
            'download_state': estado,
            'motivo_da_falha': _nao_sei(d.get('FAILURE_REASON')),
            'bytes': d.get('BYTES') if isinstance(d.get('BYTES'), int) else None,
            'sha256': sha,
            'media_type': _nao_sei(d.get('MEDIA_TYPE')),
            'storage_path': objeto,   # None quando os bytes ainda não foram preservados
            'captured_at': _nao_sei(d.get('CAPTURED_AT')),
            'source_url': d['URL'],
        })
        if objeto:
            linhas['RAW_ASSET'].append({
                'run_id': run_id, 'storage_path': objeto,
                'media_type': d.get('MEDIA_TYPE') or 'application/pdf',
                'bytes': d['BYTES'], 'sha256': sha,
                'captured_at': d.get('CAPTURED_AT') or fonte_versao,
                'source_url': d['URL'],
            })

    for r in art['CROP_RELATIONS']:
        linhas['CULTIVO'].append({
            'product_id': r['PRODUCT_ID'], 'rotulo_publicado': r['CROP'],
            'rotulo_oficial': r['CROP'], 'mapa_id_cultivo': cid(r['CROP']),
            'origem_declaracao': r['DECLARATION_SOURCE'],
            'qualidade_do_casamento': r.get('CROP_MATCH_QUALITY') or 'EXACT_OFFICIAL_LABEL',
            'par_derivavel': bool(r.get('PAIR_DERIVABLE')),
        })
    for r in art['ISSUE_RELATIONS']:
        linhas['AGENTE'].append({
            'product_id': r['PRODUCT_ID'], 'rotulo_publicado': r['ISSUE'],
            'rotulo_oficial': r['ISSUE'], 'mapa_id_plaga': iid(r['ISSUE']),
            'qualidade_do_casamento': r.get('ISSUE_MATCH_QUALITY') or 'EXACT_OFFICIAL_LABEL',
            'par_derivavel': bool(r.get('PAIR_DERIVABLE')),
        })
    for a in art.get('AMBIGUOUS_TERMS') or []:
        linhas['AMBIGUO'].append({
            'product_id': a['PRODUCT_ID'], 'eixo': a['EIXO'],
            'termo_na_pagina': a['TERMO_NA_PAGINA'],
            'rotulos_candidatos': a.get('HEAD_TERM_CANDIDATES') or a.get('ROTULOS') or [],
            'porque': a.get('PORQUE') or 'termo casa mais de um rotulo oficial',
        })

    vered = {(l['PRODUCT_ID'], l['CROP'], l['ISSUE']): l for l in (conf.get('LINHAS') or [])}
    for r in art['CROP_ISSUE_RELATIONS']:
        v = vered.get((r['PRODUCT_ID'], r['CROP'], r['ISSUE'])) or {}
        conf_estado = r.get('MAPA_CONFIRMATION') or 'ADAMA_ONLY_NOT_TESTED'
        ancora = r.get('ANCHOR') or {}
        linhas['PAR'].append({
            'product_id': r['PRODUCT_ID'],
            'cultivo_rotulo': r['CROP'], 'agente_rotulo': r['ISSUE'],
            'mapa_id_cultivo_vocab': cid(r['CROP']), 'mapa_id_plaga_vocab': iid(r['ISSUE']),
            'par_origem': r.get('PAIR_ORIGIN') or 'SAME_TABLE_ROW',
            'ancora_secao': ancora.get('PAGE_SECTION') or 'NAO_DECLARADA',
            'ancora_tabela': ancora.get('TABLE_INDEX'),
            'ancora_linha': ancora.get('ROW_INDEX'),
            'ancora_texto': ancora.get('ROW_TEXT') or '',
            'dose': _nao_sei(r.get('DOSE')),
            'bbch_de': _nao_sei(r.get('BBCH_FROM')), 'bbch_ate': _nao_sei(r.get('BBCH_TO')),
            'n_aplicacoes': _nao_sei(r.get('APPLICATION_COUNT')),
            'intervalo_dias': _nao_sei(r.get('INTERVAL_DAYS')),
            'volume_calda': _nao_sei(r.get('WATER_VOLUME')),
            'prazo_seguranca': _nao_sei(r.get('PRE_HARVEST_INTERVAL_DAYS')),
            'confirmacao_mapa': conf_estado,
            'mapa_id_cultivo': v.get('MAPA_ID_CULTIVO'),
            'mapa_id_plaga': v.get('MAPA_ID_PLAGA'),
            'mapa_registros_no_par': v.get('MAPA_REGISTROS_NO_PAR'),
            'mapa_registro_casado': v.get('REGISTRATION_ID_NA_FICHA'),
            'mapa_titular': v.get('MAPA_TITULAR'), 'mapa_estado': v.get('MAPA_ESTADO'),
            'mapa_servidor_ts': v.get('MAPA_SERVIDOR_TIMESTAMP'),
            'nivel_evidencia_final': ('REGULATORY_FACT'
                                      if conf_estado == 'ADAMA_CLAIM_MAPA_CONFIRMED'
                                      else 'MANUFACTURER_TECHNICAL_CLAIM'),
        })

    for r in art.get('CROP_DOSE_RELATIONS') or []:
        ancora = r.get('ANCHOR') or {}
        linhas['DOSE'].append({
            'product_id': r['PRODUCT_ID'], 'cultivo_rotulo': r['CROP'],
            'mapa_id_cultivo': cid(r['CROP']),
            'dose': r['DOSE'], 'dose_unidade_origem': r['DOSE_UNIT_SOURCE'],
            'bbch_de': _nao_sei(r.get('BBCH_FROM')), 'bbch_ate': _nao_sei(r.get('BBCH_TO')),
            'volume_calda': _nao_sei(r.get('WATER_VOLUME')),
            'n_aplicacoes': _nao_sei(r.get('APPLICATION_COUNT')),
            'intervalo_dias': _nao_sei(r.get('INTERVAL_DAYS')),
            'prazo_seguranca': _nao_sei(r.get('PRE_HARVEST_INTERVAL_DAYS')),
            'ancora_secao': ancora.get('PAGE_SECTION') or 'NAO_DECLARADA',
            'ancora_tabela': ancora.get('TABLE_INDEX'),
            'ancora_linha': ancora.get('ROW_INDEX'),
            'ancora_texto': ancora.get('ROW_TEXT') or '',
            'porque_nao_ha_par': r['PORQUE_NAO_HA_PAR'],
        })

    for j in art.get('APPLICATION_WINDOWS') or []:
        ancora = j.get('ANCHOR') or {}
        linhas['JANELA'].append({
            'product_id': j['PRODUCT_ID'],
            'cultivo_rotulo': _nao_sei(j.get('CROP')),
            'agente_rotulo': _nao_sei(j.get('ISSUE')),
            'bbch_de': _nao_sei(j.get('BBCH_FROM')), 'bbch_ate': _nao_sei(j.get('BBCH_TO')),
            'n_aplicacoes': _nao_sei(j.get('APPLICATION_COUNT')),
            'intervalo_dias': _nao_sei(j.get('INTERVAL_DAYS')),
            'marcadores': j.get('TIMING_FLAGS') or [],
            'ancora_secao': ancora.get('PAGE_SECTION') or 'NAO_DECLARADA',
            'ancora_texto': ancora.get('ROW_TEXT') or '',
        })

    for m in art['MODES_OF_ACTION']:
        linhas['MOA'].append({'product_id': m['PRODUCT_ID'], 'esquema': m['SCHEME'],
                              'codigo': m['CODE']})
    for c in art['CLAIMS']:
        linhas['CLAIM'].append({
            'product_id': c['PRODUCT_ID'], 'claim_id': c['CLAIM_ID'],
            'classe': c['CLAIM_TYPE'], 'texto': c['CLAIM_TEXT_SHORT'],
            'secao': _nao_sei(c.get('PAGE_SECTION')),
            'cultivo_rotulo': _nao_sei(c.get('CROP')),
            'agente_rotulo': _nao_sei(c.get('ISSUE')),
        })
    for t in art.get('TECHNOLOGIES') or []:
        linhas['TECNOLOGIA'].append({
            'product_id': t['PRODUCT_ID'], 'nome': t['TECHNOLOGY_NAME'],
            'marcador': t['MARCADOR'], 'porque_entrou': t['PORQUE_ENTROU']})
    for r in art.get('PRODUCT_RELATIONS') or []:
        linhas['RELACAO'].append({
            'product_id': r['PRODUCT_ID'],
            'produto_relacionado': r['RELATED_PRODUCT_ID'],
            'nome_relacionado': r['RELATED_PRODUCT_NAME'],
            'tipo': r['RELATION_TYPE'],
            'frase_que_sustenta': None})

    for l in (art['REGULATORY_CROSSWALK'].get('LINHAS') or []):
        estado = l.get('ESTADO')
        if not estado:
            continue
        linhas['CROSSWALK'].append({
            'product_id': l.get('PRODUCT_ID'),
            'registration_id_texto': _nao_sei(l.get('REG')),
            'estado': estado,
            'evidencia': l.get('EVIDENCIA') or 'nao declarada',
        })

    return linhas


# ── SQL ──────────────────────────────────────────────────────────────────────

CAB = """-- ═══════════════════════════════════════════════════════════════════════
-- IMPORTAÇÃO — catálogo público ADAMA España, captura de %(cap)s
--
-- Gerado por scripts/catalogo_importar.py --sql a partir de
-- data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json. NÃO editar à mão: edite o
-- artefato e gere de novo, senão as duas verdades divergem.
--
-- IDEMPOTENTE: todo INSERT tem ON CONFLICT DO NOTHING sobre chave natural.
-- Rodar duas vezes com a mesma fonte_versao insere 0 linhas na segunda.
--
-- NÃO HÁ update, delete nem upsert que sobrescreva. Fonte nova entra como
-- CAPTURA NOVA, ao lado — histórico não se reescreve.
--
-- Exige: migrations 001-010 aplicadas.
-- ═══════════════════════════════════════════════════════════════════════
begin;

"""


def gerar_sql(L):
    cap = L['CAPTURA']
    run = L['RUN']
    out = [CAB % {'cap': cap['capturado_em']}]

    out.append("-- 1 · a execução desta IMPORTAÇÃO (started_at é de agora, não da captura)\n"
               "insert into public.collection_run\n"
               "  (run_id, platform, actor, mission, source_country, started_at,\n"
               "   item_count_raw, item_count_normalized, status, capture_method,\n"
               "   source_version, rule_version)\n"
               "values (%s, %s, %s, %s, %s, now(), %s, %s, 'concluida', %s, %s, %s)\n"
               "on conflict (run_id) do nothing;\n"
               % (q(run['run_id']), q(run['platform']), q(run['actor']), q(run['mission']),
                  q(run['source_country']), q(run['item_count_raw']),
                  q(run['item_count_normalized']), q(run['capture_method']),
                  q(run['source_version']), q(run['rule_version'])))

    out.append("\n-- 2 · a captura. capturado_em é a hora REAL da leitura do site;\n"
               "--     importado_em é now(). As duas não podem colapsar.\n"
               "insert into public.catalogo_captura\n"
               "  (run_id, pais, fabricante, catalogo_url, capturado_em, metodo_de_captura,\n"
               "   fonte_versao, rule_version, total_no_catalogo, enumeracao_completa, e_baseline)\n"
               "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n"
               "on conflict (pais, fabricante, fonte_versao) do nothing;\n"
               % (q(run['run_id']), q(cap['pais']), q(cap['fabricante']),
                  q(cap['catalogo_url']), q(cap['capturado_em']), q(cap['metodo_de_captura']),
                  q(cap['fonte_versao']), q(cap['rule_version']), q(cap['total_no_catalogo']),
                  q(cap['enumeracao_completa']), q(cap['e_baseline'])))

    def capsel():
        return ("(select id from public.catalogo_captura where pais=%s and fabricante=%s "
                "and fonte_versao=%s)" % (q(cap['pais']), q(cap['fabricante']),
                                          q(cap['fonte_versao'])))

    def prodsel(pid):
        return ("(select id from public.catalogo_produto where captura_id=%s and "
                "product_id=%s)" % (capsel(), q(pid)))

    def cropsel(mapa_id):
        return ('null' if not mapa_id else
                "(select id from public.crop where mapa_id_cultivo=%d)" % mapa_id)

    def issuesel(mapa_id):
        return ('null' if not mapa_id else
                "(select id from public.issue where mapa_id_plaga=%d)" % mapa_id)

    out.append("\n-- 3 · produtos (%d)\n" % len(L['PRODUTO']))
    for p in L['PRODUTO']:
        out.append("insert into public.catalogo_produto (captura_id, pais, product_id,"
                   " nome_publicado, categoria, pagina_url, registration_id, formulacao,"
                   " composicao_texto) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                   " on conflict (captura_id, product_id) do nothing;\n"
                   % (capsel(), q(p['pais']), q(p['product_id']), q(p['nome_publicado']),
                      q(p['categoria']), q(p['pagina_url']), q(p['registration_id']),
                      q(p['formulacao']), q(p['composicao_texto'])))

    if L['RAW_ASSET']:
        out.append("\n-- 4 · raw_asset dos documentos VERIFICADOS no Storage (%d)\n"
                   % len(L['RAW_ASSET']))
        for a in L['RAW_ASSET']:
            out.append("insert into public.raw_asset (run_id, storage_path, media_type,"
                       " bytes, sha256, captured_at, source_url)"
                       " values (%s,%s,%s,%s,%s,%s,%s)"
                       " on conflict (storage_path) do nothing;\n"
                       % (q(a['run_id']), q(a['storage_path']), q(a['media_type']),
                          q(a['bytes']), q(a['sha256']), q(a['captured_at']),
                          q(a['source_url'])))
    else:
        out.append("\n-- 4 · raw_asset: NENHUM. Nenhum byte foi verificado no Storage\n"
                   "--     ainda, e documento só aponta para raw_asset depois de\n"
                   "--     VERIFIED. Rode storage_preservar.py --enviar antes.\n")

    out.append("\n-- 5 · documentos (%d). FAILED nunca aponta raw_asset.\n"
               % len(L['DOCUMENTO']))
    for d in L['DOCUMENTO']:
        ra = ('null' if not d['storage_path'] else
              "(select id from public.raw_asset where storage_path=%s)" % q(d['storage_path']))
        out.append("insert into public.catalogo_produto_documento (produto_id, document_id,"
                   " tipo, tipo_evidencia, prova_de_que_e_documento, url, pagina_origem,"
                   " nome_arquivo, data_visivel, http_status, download_state,"
                   " motivo_da_falha, bytes, sha256, media_type, raw_asset_id)"
                   " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, document_id) do nothing;\n"
                   % (prodsel(d['product_id']), q(d['document_id']), q(d['tipo']),
                      q(d['tipo_evidencia']), q(d['prova_de_que_e_documento']), q(d['url']),
                      q(d['pagina_origem']), q(d['nome_arquivo']), q(d['data_visivel']),
                      q(d['http_status']), q(d['download_state']), q(d['motivo_da_falha']),
                      q(d['bytes']), q(d['sha256']), q(d['media_type']), ra))

    out.append("\n-- 6 · cultivos (%d). origem_declaracao separa DECLARADO de CITADO.\n"
               % len(L['CULTIVO']))
    for c in L['CULTIVO']:
        out.append("insert into public.catalogo_produto_cultivo (produto_id,"
                   " rotulo_publicado, crop_id, rotulo_oficial, origem_declaracao,"
                   " qualidade_do_casamento, par_derivavel)"
                   " values (%s,%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, rotulo_publicado, origem_declaracao)"
                   " do nothing;\n"
                   % (prodsel(c['product_id']), q(c['rotulo_publicado']),
                      cropsel(c['mapa_id_cultivo']), q(c['rotulo_oficial']),
                      q(c['origem_declaracao']), q(c['qualidade_do_casamento']),
                      q(c['par_derivavel'])))

    out.append("\n-- 7 · agentes (%d)\n" % len(L['AGENTE']))
    for a in L['AGENTE']:
        out.append("insert into public.catalogo_produto_agente (produto_id,"
                   " rotulo_publicado, issue_id, rotulo_oficial, qualidade_do_casamento,"
                   " par_derivavel) values (%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, rotulo_publicado) do nothing;\n"
                   % (prodsel(a['product_id']), q(a['rotulo_publicado']),
                      issuesel(a['mapa_id_plaga']), q(a['rotulo_oficial']),
                      q(a['qualidade_do_casamento']), q(a['par_derivavel'])))

    out.append("\n-- 8 · termos ambiguos (%d) — listados, nunca resolvidos por palpite\n"
               % len(L['AMBIGUO']))
    for a in L['AMBIGUO']:
        out.append("insert into public.catalogo_termo_ambiguo (produto_id, eixo,"
                   " termo_na_pagina, rotulos_candidatos, porque)"
                   " values (%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, eixo, termo_na_pagina) do nothing;\n"
                   % (prodsel(a['product_id']), q(a['eixo']), q(a['termo_na_pagina']),
                      qj(a['rotulos_candidatos']), q(a['porque'])))

    out.append("\n-- 9 · pares cultivo x agente (%d) — TODOS com ancora de linha\n"
               % len(L['PAR']))
    for r in L['PAR']:
        out.append("insert into public.catalogo_produto_cultivo_agente (produto_id,"
                   " cultivo_rotulo, agente_rotulo, crop_id, issue_id, par_origem,"
                   " ancora_secao, ancora_tabela, ancora_linha, ancora_texto, dose,"
                   " bbch_de, bbch_ate, n_aplicacoes, intervalo_dias, volume_calda,"
                   " prazo_seguranca, confirmacao_mapa, mapa_id_cultivo, mapa_id_plaga,"
                   " mapa_registros_no_par, mapa_registro_casado, mapa_titular,"
                   " mapa_estado, mapa_servidor_ts, nivel_evidencia_final)"
                   " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
                   "%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, cultivo_rotulo, agente_rotulo) do nothing;\n"
                   % (prodsel(r['product_id']), q(r['cultivo_rotulo']), q(r['agente_rotulo']),
                      cropsel(r['mapa_id_cultivo_vocab']), issuesel(r['mapa_id_plaga_vocab']),
                      q(r['par_origem']), q(r['ancora_secao']), q(r['ancora_tabela']),
                      q(r['ancora_linha']), q(r['ancora_texto']), q(r['dose']),
                      q(r['bbch_de']), q(r['bbch_ate']), q(r['n_aplicacoes']),
                      q(r['intervalo_dias']), q(r['volume_calda']), q(r['prazo_seguranca']),
                      q(r['confirmacao_mapa']), q(r['mapa_id_cultivo']),
                      q(r['mapa_id_plaga']), q(r['mapa_registros_no_par']),
                      q(r['mapa_registro_casado']), q(r['mapa_titular']),
                      q(r['mapa_estado']), q(r['mapa_servidor_ts']),
                      q(r['nivel_evidencia_final'])))

    out.append("\n-- 10 · cultivo x DOSE (%d) — tabela separada; nao e par\n" % len(L['DOSE']))
    for r in L['DOSE']:
        out.append("insert into public.catalogo_produto_cultivo_dose (produto_id,"
                   " cultivo_rotulo, crop_id, dose, dose_unidade_origem, bbch_de, bbch_ate,"
                   " volume_calda, n_aplicacoes, intervalo_dias, prazo_seguranca,"
                   " ancora_secao, ancora_tabela, ancora_linha, ancora_texto,"
                   " porque_nao_ha_par)"
                   " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, cultivo_rotulo, ancora_tabela, ancora_linha)"
                   " do nothing;\n"
                   % (prodsel(r['product_id']), q(r['cultivo_rotulo']),
                      cropsel(r['mapa_id_cultivo']), q(r['dose']),
                      q(r['dose_unidade_origem']), q(r['bbch_de']), q(r['bbch_ate']),
                      q(r['volume_calda']), q(r['n_aplicacoes']), q(r['intervalo_dias']),
                      q(r['prazo_seguranca']), q(r['ancora_secao']), q(r['ancora_tabela']),
                      q(r['ancora_linha']), q(r['ancora_texto']), q(r['porque_nao_ha_par'])))

    out.append("\n-- 11 · janelas publicadas (%d). Ausencia NAO vira linha CLOSED.\n"
               % len(L['JANELA']))
    for j in L['JANELA']:
        out.append("insert into public.catalogo_produto_janela_aplicacao (produto_id,"
                   " cultivo_rotulo, agente_rotulo, bbch_de, bbch_ate, n_aplicacoes,"
                   " intervalo_dias, marcadores, ancora_secao, ancora_texto)"
                   " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);\n"
                   % (prodsel(j['product_id']), q(j['cultivo_rotulo']),
                      q(j['agente_rotulo']), q(j['bbch_de']), q(j['bbch_ate']),
                      q(j['n_aplicacoes']), q(j['intervalo_dias']), qj(j['marcadores']),
                      q(j['ancora_secao']), q(j['ancora_texto'])))

    out.append("\n-- 12 · substancias (%d). texto_publicado e a fonte; normalizacao virá\n"
               "--      depois, e exige declarar a regra.\n" % len(L['SUBSTANCIA']))
    for s in L['SUBSTANCIA']:
        out.append("insert into public.catalogo_produto_substancia (produto_id,"
                   " texto_publicado, nome_normalizado, regra_normalizacao, concentracao,"
                   " concentracao_unidade, codigo_formulacao)"
                   " values (%s,%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, texto_publicado) do nothing;\n"
                   % (prodsel(s['product_id']), q(s['texto_publicado']),
                      q(s['nome_normalizado']), q(s['regra_normalizacao']),
                      q(s['concentracao']), q(s['concentracao_unidade']),
                      q(s['codigo_formulacao'])))

    out.append("\n-- 13 · modos de acao (%d)\n" % len(L['MOA']))
    for m in L['MOA']:
        out.append("insert into public.catalogo_produto_modo_acao (produto_id, esquema,"
                   " codigo) values (%s,%s,%s)"
                   " on conflict (produto_id, esquema, codigo) do nothing;\n"
                   % (prodsel(m['product_id']), q(m['esquema']), q(m['codigo'])))

    out.append("\n-- 14 · claims (%d) — tres classes, nenhuma vira fato\n" % len(L['CLAIM']))
    for c in L['CLAIM']:
        out.append("insert into public.catalogo_produto_claim (produto_id, claim_id,"
                   " classe, texto, secao, cultivo_rotulo, agente_rotulo)"
                   " values (%s,%s,%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, claim_id) do nothing;\n"
                   % (prodsel(c['product_id']), q(c['claim_id']), q(c['classe']),
                      q(c['texto']), q(c['secao']), q(c['cultivo_rotulo']),
                      q(c['agente_rotulo'])))

    out.append("\n-- 15 · tecnologia (%d) e relacao entre produtos (%d)\n"
               % (len(L['TECNOLOGIA']), len(L['RELACAO'])))
    for t in L['TECNOLOGIA']:
        out.append("insert into public.catalogo_produto_tecnologia (produto_id, nome,"
                   " marcador, porque_entrou) values (%s,%s,%s,%s)"
                   " on conflict (produto_id, nome) do nothing;\n"
                   % (prodsel(t['product_id']), q(t['nome']), q(t['marcador']),
                      q(t['porque_entrou'])))
    for r in L['RELACAO']:
        out.append("insert into public.catalogo_produto_relacao (produto_id,"
                   " produto_relacionado_id, nome_relacionado, tipo, frase_que_sustenta)"
                   " values (%s,%s,%s,%s,%s)"
                   " on conflict (produto_id, produto_relacionado_id, tipo) do nothing;\n"
                   % (prodsel(r['product_id']), prodsel(r['produto_relacionado']),
                      q(r['nome_relacionado']), q(r['tipo']), q(r['frase_que_sustenta'])))

    out.append("\n-- 16 · crosswalk (%d) — relacao, nao fusao\n" % len(L['CROSSWALK']))
    for c in L['CROSSWALK']:
        prod = 'null' if not c['product_id'] else prodsel(c['product_id'])
        reg = ('null' if not c['registration_id_texto'] else
               "(select id from public.registro_regulatorio where pais='ES' and "
               "registration_id=%s order by fonte_versao desc limit 1)"
               % q(c['registration_id_texto']))
        out.append("insert into public.catalogo_registro_crosswalk (captura_id, produto_id,"
                   " registro_id, registration_id_texto, estado, evidencia)"
                   " values (%s,%s,%s,%s,%s,%s);\n"
                   % (capsel(), prod, reg, q(c['registration_id_texto']), q(c['estado']),
                      q(c['evidencia'])))

    out.append("\ncommit;\n")
    return ''.join(out)


def contagens(L):
    return {k: (len(v) if isinstance(v, list) else 1) for k, v in L.items()}


if __name__ == '__main__':
    L = normalizar()
    if '--linhas' in sys.argv:
        with open(LINHAS_OUT, 'w', encoding='utf-8') as f:
            json.dump({'CONTAGENS': contagens(L), 'LINHAS': L}, f,
                      ensure_ascii=False, indent=1)
        print('LINHAS %s' % os.path.relpath(LINHAS_OUT, ROOT))
        for k, v in sorted(contagens(L).items()):
            print('  %-12s %s' % (k, v))
        sys.exit(0)
    if '--sql' in sys.argv:
        os.makedirs(os.path.dirname(SQL_OUT), exist_ok=True)
        sql = gerar_sql(L)
        with open(SQL_OUT, 'w', encoding='utf-8') as f:
            f.write(sql)
        print('SQL %s  %d bytes  %d comandos'
              % (os.path.relpath(SQL_OUT, ROOT), len(sql), sql.count(';')))
        sys.exit(0)
    if '--aplicar' in sys.argv:
        db = (os.environ.get('SUPABASE_DB_URL') or '').strip()
        if not db:
            print('SUPABASE_DB_URL ausente — nada aplicado.')
            sys.exit(2)
        import shutil
        import subprocess
        if not shutil.which('psql'):
            print('psql nao instalado nesta maquina — nada aplicado.')
            sys.exit(3)
        if not os.path.exists(SQL_OUT):
            print('rode --sql antes')
            sys.exit(4)
        r = subprocess.run(['psql', db, '-v', 'ON_ERROR_STOP=1', '-f', SQL_OUT],
                           capture_output=True, text=True)
        # nunca imprimir a URL do banco: ela carrega a senha
        print((r.stdout or '')[-2000:].replace(db, '<OMITIDO>'))
        if r.returncode:
            print((r.stderr or '')[-2000:].replace(db, '<OMITIDO>'))
        sys.exit(r.returncode)
    print(__doc__)
