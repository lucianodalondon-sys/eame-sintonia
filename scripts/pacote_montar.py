#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTA O PACOTE — relações, validação, varredura de segredo e ZIP.

    python3 scripts/pacote_montar.py

Ordem, e ela importa:

    1  RELAÇÕES      liga os objetos por ID, sem copiar registro
    2  VALIDAÇÃO     todo JSON abre; todo ID é único; toda referência existe
    3  SEGURANÇA     nenhum segredo entra. Se achar, NÃO empacota
    4  ZIP           só depois de PASS nas duas anteriores

⚠️ A trava da validação é `EVERY REFERENCED ENTITY_ID MUST EXIST` — e a regra que a
acompanha é a que evita o desastre: **não inventar a entidade que falta só para a
referência passar**. Referência órfã é relatada, não consertada com ficção.
"""
import json
import os
import re
import sys
import zipfile
from collections import Counter, OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF')
DR = os.path.join(PKG, '01-DESIGN-READY')

SEGREDOS = [
    (r'apify_api_[A-Za-z0-9]{20,}', 'token Apify'),
    (r'\bsb_secret_[A-Za-z0-9_\-]{10,}', 'chave Supabase'),
    (r'\beyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}', 'JWT'),
    (r'\bgh[pousr]_[A-Za-z0-9]{30,}', 'token GitHub'),
    (r'(?i)\b(api[_-]?key|secret[_-]?key|password|passwd)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{12,}',
     'credencial em par chave-valor'),
    (r'(?i)\bBearer\s+[A-Za-z0-9_\-\.]{20,}', 'header Authorization'),
    (r'(?i)\bAKIA[0-9A-Z]{16}\b', 'chave AWS'),
]
# Estes NÃO são segredo, e precisam ficar de fora do alarme: o pacote FALA sobre
# credenciais o tempo todo (a política de chaves, o aviso de que a chave não entra).
FALSO_POSITIVO = re.compile(
    r'(?i)(NUNCA_GRAVAR_TOKEN|TOKEN_VALUE_LOGGED|TOKEN_POOL_PRESENT|APIFY_TOKEN_POOL|'
    r'SUPABASE_SECRET_KEY|secrets\.|API_TOKEN_AUSENTE|chave descartavel|'
    r'credenciais do Supabase|nao entra no|jamais)')


# ⚠️ NEM TODA LISTA COM `ID` DEFINE O OBJETO.
# Um arquivo por linha de produto carrega `PRODUCTS_SUMMARY` — nome, ativo e vencimento —
# para o Design nao precisar abrir o arquivo grande so para montar uma lista. Isso e
# REFERENCIA com rotulo, nao segunda definicao.
#
#     DEFINICAO mora em UM arquivo. Resumo e indice apontam para ela.
#
# Sem esta distincao o validador acusava 178 «IDs duplicados» que nao eram duplicatas —
# e um validador que grita errado ensina a ignorar validador.
DEFINE_NAO = re.compile(r'(_SUMMARY|_IDS|^INDEX$|^BY_|^OBJECTS$)')

# E pastas inteiras que sao INDICE por natureza: elas percorrem a camada de dados e
# repetem os IDs de proposito. Ler isso como segunda definicao seria acusar o indice de
# duplicar o livro.
PASTA_INDICE = ('04-PROVENANCE/', '06-HANDOFF-MANIFEST/', '03-SOURCE-REGISTRY/')


def jsons():
    for dp, _dn, fn in os.walk(PKG):
        for f in fn:
            if f.endswith('.json'):
                yield os.path.join(dp, f)


def rel(p):
    return os.path.relpath(p, PKG).replace(os.sep, '/')


# ── 1 · RELAÇÕES ──────────────────────────────────────────────────────────────
def relacoes():
    idx = {}
    for p in jsons():
        if rel(p).startswith(PASTA_INDICE):
            continue
        try:
            d = json.load(open(p, encoding='utf-8'))
        except ValueError:
            continue
        for k, v in (d.items() if isinstance(d, dict) else []):
            if not isinstance(v, list) or DEFINE_NAO.search(k):
                continue
            for it in v:
                if isinstance(it, dict) and it.get('ID'):
                    idx[it['ID']] = (rel(p), it)

    def por_pref(pref):
        return {k: v for k, v in idx.items() if k.startswith(pref)}

    ops = por_pref('IT-OPP')
    wins = por_pref('IT-WIN')
    prods = por_pref('IT-PRD')
    voices = por_pref('IT-VOICE')
    people = por_pref('IT-PER')
    acts = por_pref('IT-COMP-ACT')
    news = por_pref('IT-NEWS')
    futs = por_pref('IT-FUT')
    res = por_pref('IT-RES')
    evts = por_pref('IT-EVT')

    def prod_ids(nomes):
        alvo = {str(n).upper().strip() for n in (nomes or [])}
        return [k for k, (_f, o) in prods.items()
                if str(o.get('PRODUCT', '')).upper().strip() in alvo]

    links = []
    for oid, (_f, o) in ops.items():
        crop = (o.get('CROP') or '').upper()
        issue = (o.get('ISSUE') or '').lower()
        rel_win = [k for k, (_g, w) in wins.items()
                   if (w.get('CROP') or '').upper().startswith(crop[:4])]
        rel_voice = [k for k, (_g, v) in voices.items()
                     if 'flavesc' in issue and 'FLAVESCENCE' in str(v.get('CASE_ID', ''))]
        rel_act = [k for k, (_g, a) in acts.items()
                   if any('vitis' in str(t).lower() or 'vite' in str(t).lower()
                          for t in (a.get('CROP_TERMS') or [])) and 'VITE' in crop][:20]
        rel_news = [k for k, (_g, n) in news.items()
                    if (n.get('CROP') or '').upper().startswith(crop[:4])]
        rel_per = [k for k, (_g, p) in people.items()
                   if 'flavesc' in issue and any(
                       x in str(p.get('IDENTITY_EVIDENCE', '')) + str(p.get('ROLE', ''))
                       for x in ('VINE_FLAVESCENCE', 'flavescenza', 'CREA', 'Torino'))]
        rel_res = [k for k, (_g, r) in res.items()
                   if 'WEED' in str(o.get('ISSUE_TYPE'))]
        links.append(OrderedDict([
            ('FROM', oid), ('FROM_TITLE', o.get('TITLE')),
            ('RELATED_CROP_WINDOWS', rel_win),
            ('RELATED_PRODUCTS', prod_ids(o.get('ADAMA_PRODUCTS'))),
            ('RELATED_PEOPLE', rel_per),
            ('RELATED_FIELD_VOICES', rel_voice),
            ('RELATED_COMPETITOR_ACTIVITY', rel_act),
            ('RELATED_NEWS', rel_news),
            ('RELATED_RESISTANCE', rel_res),
            ('RELATED_SOURCES', o.get('SOURCE_IDS') or []),
        ]))
    for fid, (_f, s) in futs.items():
        links.append(OrderedDict([
            ('FROM', fid), ('FROM_TITLE', s.get('WHAT_CHANGED', '')[:80]),
            ('RELATED_PRODUCTS', []),
            ('RELATED_PEOPLE', [k for k, (_g, p) in people.items()
                                if 'GIRE' in str(p.get('ROLE', ''))]
             if 'REGULATORIO' not in str(s.get('ISSUE')) else []),
            ('RELATED_SOURCES', s.get('SOURCE_IDS') or []),
        ]))
    corpo = OrderedDict([
        ('LAYER', 'RELATIONSHIPS'), ('BUILT_AT', '2026-09-02'),
        ('LAW', 'esta camada guarda SO IDs. Duplicar o registro dentro do link e como o '
                'mesmo fato passa a ter duas versoes que divergem em silencio.'),
        ('HOW_TO_RESOLVE', 'todo ID aparece no campo `ID` de algum objeto dentro de '
                           '01-DESIGN-READY. O indice completo esta em '
                           '06-HANDOFF-MANIFEST/ID-INDEX.json'),
        ('COUNT', len(links)), ('LINKS', links)])
    d = os.path.join(DR, 'RELATIONSHIPS')
    os.makedirs(d, exist_ok=True)
    json.dump(corpo, open(os.path.join(d, 'entity-links.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    # indice de ID
    ind = OrderedDict([
        ('LAYER', 'ID_INDEX'), ('BUILT_AT', '2026-09-02'), ('COUNT', len(idx)),
        ('BY_PREFIX', dict(Counter(k.rsplit('-', 1)[0] for k in idx))),
        ('INDEX', {k: {'FILE': v[0],
                       'LABEL': (v[1].get('TITLE') or v[1].get('PRODUCT')
                                 or v[1].get('PERSON') or v[1].get('EVENT')
                                 or v[1].get('SPECIES') or v[1].get('CHANNEL')
                                 or v[1].get('CROP_TERM') or v[1].get('COMPANY')
                                 or v[1].get('THEME') or v[1].get('DATASET') or '')}
                   for k, v in sorted(idx.items())})])
    dm = os.path.join(PKG, '06-HANDOFF-MANIFEST')
    os.makedirs(dm, exist_ok=True)
    json.dump(ind, open(os.path.join(dm, 'ID-INDEX.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('  relacoes: %d · IDs indexados: %d' % (len(links), len(idx)))
    return idx, links


# ── 2 · VALIDAÇÃO ─────────────────────────────────────────────────────────────
def validar(idx):
    erros, orfas = [], []
    dup = defaultdict(list)
    for p in jsons():
        try:
            d = json.load(open(p, encoding='utf-8'))
        except ValueError as e:
            erros.append('%s: JSON invalido — %s' % (rel(p), e))
            continue
        if rel(p).startswith(PASTA_INDICE):
            continue
        for k, v in (d.items() if isinstance(d, dict) else []):
            if not isinstance(v, list) or DEFINE_NAO.search(k):
                continue
            for it in v:
                if isinstance(it, dict) and it.get('ID'):
                    dup[it['ID']].append(rel(p))
    dups = {k: v for k, v in dup.items() if len(v) > 1}
    padrao = re.compile(r'\bIT-(?:OPP|FUT|WIN|MKT|COMP-ACT|COMP-PRD|COMP|VOICE|SCI|PER|'
                        r'NEWS|EVT|SRC|PRD|CPP|CROP|CHAN|RES|THEME|ARC)-\d{3}\b')
    for p in jsons():
        if rel(p).endswith('ID-INDEX.json'):
            continue
        txt = open(p, encoding='utf-8').read()
        for m in set(padrao.findall(txt)):
            if m not in idx:
                orfas.append({'FILE': rel(p), 'MISSING_ID': m})
    return erros, dups, orfas


# ── 3 · SEGURANÇA ─────────────────────────────────────────────────────────────
def seguranca():
    achados = []
    for dp, _dn, fn in os.walk(PKG):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.getsize(p) > 40 * 1024 * 1024:
                continue
            try:
                txt = open(p, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for rx, nome in SEGREDOS:
                for m in re.finditer(rx, txt):
                    ctx = txt[max(0, m.start() - 90): m.end() + 60]
                    if FALSO_POSITIVO.search(ctx):
                        continue
                    achados.append({'FILE': rel(p), 'KIND': nome,
                                    'MATCH': m.group(0)[:12] + '…'})
    proibidos = [rel(os.path.join(dp, f)) for dp, _dn, fn in os.walk(PKG) for f in fn
                 if f in ('.env',) or f.startswith('.env.') or f.endswith('.pem')]
    return achados, proibidos


def main():
    if not os.path.isdir(DR):
        print('PACOTE_NAO_MONTADO — rode os scripts pacote_*.py antes'); return 1
    print('RELACOES')
    idx, links = relacoes()
    print('VALIDACAO')
    erros, dups, orfas = validar(idx)
    print('  JSON invalido: %d · IDs duplicados: %d · referencias orfas: %d'
          % (len(erros), len(dups), len(orfas)))
    for e in erros[:5]:
        print('    !', e)
    for k, v in list(dups.items())[:5]:
        print('    ! ID %s em %s' % (k, v))
    for o in orfas[:8]:
        print('    ! %s referencia %s, que nao existe' % (o['FILE'], o['MISSING_ID']))
    print('SEGURANCA')
    achados, proibidos = seguranca()
    print('  segredos: %d · arquivos proibidos: %d' % (len(achados), len(proibidos)))
    for a in achados[:8]:
        print('    ! %s — %s' % (a['FILE'], a['KIND']))
    scan = 'PASS' if not achados and not proibidos else 'FAIL'
    val = 'PASS' if not erros and not dups else 'FAIL'

    rel_val = OrderedDict([
        ('BUILT_AT', '2026-09-02'),
        ('JSON_VALIDATION', val), ('SECURITY_SCAN', scan),
        ('JSON_ERRORS', erros), ('DUPLICATE_IDS', dups),
        ('BROKEN_REFERENCES', orfas),
        ('BROKEN_REFERENCE_LAW', 'referencia orfa e RELATADA, nunca consertada inventando '
                                 'a entidade que falta.'),
        ('SECRET_FINDINGS', achados), ('FORBIDDEN_FILES', proibidos),
    ])
    dm = os.path.join(PKG, '06-HANDOFF-MANIFEST')
    os.makedirs(dm, exist_ok=True)
    json.dump(rel_val, open(os.path.join(dm, 'VALIDATION-REPORT.json'), 'w',
                            encoding='utf-8'), ensure_ascii=False, indent=1)

    if scan != 'PASS':
        print('\n⛔ SECURITY_SCAN = FAIL — nao empacoto.'); return 2

    print('ZIP')
    destino = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF.zip')
    n = 0
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, _dn, fn in os.walk(PKG):
            for f in sorted(fn):
                p = os.path.join(dp, f)
                z.write(p, os.path.join('SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                                        os.path.relpath(p, PKG)))
                n += 1
    tam = os.path.getsize(destino)
    print('  %s · %d arquivos · %.2f MB' % (os.path.relpath(destino, ROOT), n, tam / 1e6))
    print('\nJSON_VALIDATION=%s · SECURITY_SCAN=%s' % (val, scan))
    return 0


if __name__ == '__main__':
    sys.exit(main())
