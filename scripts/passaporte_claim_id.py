#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IDENTIDADE DAS AFIRMAÇÕES — medir a colisão, comparar esquemas, propor a reemissão.

SOMENTE LEITURA sobre o acervo e sobre `data/passaporte/EVENTOS.jsonl`. Este script
**nunca** escreve no log de eventos. Ele produz medição e uma proposta de reemissão;
aplicar a proposta é outro ato, com outro comando, fora desta missão.

Subcomandos
    medir      tabela completa de colisões (§1 da missão)
    comparar   os três esquemas de identidade lado a lado (§2)
    propor     a reemissão determinística, em arquivo separado (§3)

Uso
    python3 scripts/passaporte_claim_id.py medir    --passaporte <ref>
    python3 scripts/passaporte_claim_id.py comparar --passaporte <ref>
    python3 scripts/passaporte_claim_id.py propor   --passaporte <ref> --json saida.json
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import unicodedata

RULE_VERSION = 'CLAIM-ID-2026-09-06'

# O evento que declara uma afirmação, e os que dependem dela.
EV_CLAIM = 'CLAIMS_EXTRACTED'
EV_DEPENDENTES = ('ROUTED_TO_CAPABILITY', 'CONSUMED_BY_CAPABILITY', 'CONSUMPTION_BLOCKED')

CASE = re.compile(r'\b(CASE-\d{3})\b')


# ── leitura ────────────────────────────────────────────────────────────────────────

def ler_eventos(raiz):
    caminho = os.path.join(raiz, 'data', 'passaporte', 'EVENTOS.jsonl')
    if not os.path.isfile(caminho):
        raise SystemExit(f'NAO_MEDIDO — EVENTOS.jsonl ausente em {raiz}')
    with open(caminho, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def ler_casos(raiz):
    """CASE_ID -> contexto declarado (COUNTRY, CROP, REGION, TIME, SOURCES).

    Lido do documento, nunca digitado. Caso ausente vira {} — não vira suposição.
    """
    caminho = os.path.join(raiz, 'docs', 'apresentacao', 'CASOS-PARA-APRESENTACAO.md')
    if not os.path.isfile(caminho):
        return {}
    casos, atual = {}, None
    for linha in open(caminho, encoding='utf-8'):
        m = re.match(r'^### (CASE-\d+)\s*·\s*(.+)$', linha)
        if m:
            atual = m.group(1)
            casos[atual] = {'TITULO': m.group(2).strip()}
            continue
        if not atual:
            continue
        m = re.match(r'^(COUNTRY|CROP|REGION|PROBLEM|TIME|SOURCES|CROSSING):\s*(.+)$',
                     linha.strip())
        if m:
            casos[atual][m.group(1)] = m.group(2).strip()
    return casos


# ── a chave local de uma afirmação, extraída de PROVA, nunca inventada ─────────────

def chave_local(evento):
    """ASSERTION_LOCAL_KEY: o CASE_ID que a própria fonte declara.

    Procurado, em ordem, em REASON e EVIDENCE_REFERENCE. Se não houver CASE_ID em
    nenhum dos dois, devolve None — e o item entra em SEM_CHAVE_LOCAL, nunca num
    ordinal inventado.
    """
    for campo in ('REASON', 'EVIDENCE_REFERENCE'):
        m = CASE.search(str(evento.get(campo) or ''))
        if m:
            return m.group(1)
    return None


def texto_canonico(s):
    """Representação canônica de uma afirmação, para comparar e para hashear.

    NFKC + minúsculas + espaços colapsados. Deliberadamente conservadora: ela NÃO
    remove pontuação nem palavras, porque duas afirmações que só diferem num número
    são afirmações diferentes.
    """
    s = unicodedata.normalize('NFKC', str(s or '')).strip().lower()
    return re.sub(r'\s+', ' ', s)


# ── §1 · MEDIR ─────────────────────────────────────────────────────────────────────

def medir(eventos, casos):
    claims = collections.defaultdict(list)      # CLAIM_ID -> [evento CLAIMS_EXTRACTED]
    dependentes = collections.defaultdict(list)  # CLAIM_ID -> [evento de rota/consumo]
    for e in eventos:
        cid = e.get('CLAIM_ID')
        if not cid:
            continue
        if e.get('EVENT_TYPE') == EV_CLAIM:
            claims[cid].append(e)
        elif e.get('EVENT_TYPE') in EV_DEPENDENTES:
            dependentes[cid].append(e)

    linhas = []
    for cid, evs in sorted(claims.items()):
        textos = {texto_canonico(e.get('REASON')) for e in evs}
        casos_env = sorted({k for e in evs if (k := chave_local(e))})
        itens = sorted({e['ITEM_ID'] for e in evs})
        rotas = dependentes.get(cid, [])
        caps = sorted({r.get('CAPABILITY_ID') for r in rotas if r.get('CAPABILITY_ID')})

        # rota SEM chave local própria não pode ser reatribuída a um claim específico
        rotas_orfas = [r for r in rotas if chave_local(r) is None]

        if len(evs) == 1:
            classe = 'SEM_COLISAO'
        elif len(textos) == 1:
            classe = 'COLISAO_MESMO_TEXTO'
        else:
            classe = 'COLISAO_TEXTO_DIFERENTE'

        # o contexto declarado dos casos envolvidos diverge?
        divergencia = {}
        if len(casos_env) > 1:
            for eixo in ('COUNTRY', 'CROP', 'REGION', 'TIME', 'PROBLEM'):
                valores = {casos.get(c, {}).get(eixo) for c in casos_env}
                valores.discard(None)
                if len(valores) > 1:
                    divergencia[eixo] = sorted(valores)

        linhas.append({
            'CLAIM_ID': cid,
            'CLASSE': classe,
            'N_CLAIMS': len(evs),
            'N_TEXTOS_DISTINTOS': len(textos),
            'ITEM_IDS': itens,
            'CASOS': casos_env,
            'SEM_CHAVE_LOCAL': sum(1 for e in evs if chave_local(e) is None),
            'CAPACIDADES': caps,
            'N_ROTAS': len(rotas),
            'N_ROTAS_ORFAS': len(rotas_orfas),
            'DIVERGENCIA_DE_CONTEXTO': divergencia,
            'TEXTOS': sorted(str(e.get('REASON'))[:100] for e in evs),
        })
    return linhas, claims, dependentes


def resumo(linhas):
    col = [l for l in linhas if l['CLASSE'] != 'SEM_COLISAO']
    return {
        'CLAIMS_TOTAL': sum(l['N_CLAIMS'] for l in linhas),
        'CLAIM_IDS_TOTAL': len(linhas),
        'COLLIDING_IDS': len(col),
        'CLAIMS_ON_AMBIGUOUS_ID': sum(l['N_CLAIMS'] for l in col),
        'ROUTES_ON_AMBIGUOUS_ID': sum(l['N_ROTAS'] for l in col),
        'ROUTES_TOTAL': sum(l['N_ROTAS'] for l in linhas),
        'ROTAS_ORFAS_EM_ID_AMBIGUO': sum(l['N_ROTAS_ORFAS'] for l in col),
        'COLISAO_MESMO_TEXTO': sum(1 for l in col if l['CLASSE'] == 'COLISAO_MESMO_TEXTO'),
        'COLISAO_TEXTO_DIFERENTE': sum(1 for l in col
                                       if l['CLASSE'] == 'COLISAO_TEXTO_DIFERENTE'),
        'COLISAO_COM_DIVERGENCIA_DE_CONTEXTO': sum(1 for l in col
                                                   if l['DIVERGENCIA_DE_CONTEXTO']),
    }


# ── §2 · OS TRÊS ESQUEMAS ──────────────────────────────────────────────────────────

def esquema_A_estrutural(evento):
    """SOURCE + ITEM + ASSERTION_LOCAL_KEY. Legível, e depende da chave local existir."""
    chave = chave_local(evento)
    if not chave:
        return None, 'SEM_CHAVE_LOCAL'
    return f"CLAIM-{evento['ITEM_ID'].split('-', 1)[1]}-{chave}", None


def esquema_B_conteudo(evento):
    """Hash de uma representação canônica: item + texto da afirmação."""
    base = f"{evento['ITEM_ID']}|{texto_canonico(evento.get('REASON'))}"
    return 'CLAIM-' + hashlib.sha1(base.encode('utf-8')).hexdigest()[:16].upper(), None


def esquema_C_hibrido(evento):
    """ITEM + CHAVE_LOCAL + hash do conteúdo. As duas coisas, não uma ou outra.

    A chave local torna o id legível e ligável ao caso; o hash garante que duas
    afirmações diferentes sob a MESMA chave não colidam. Sem chave local, o id
    ainda nasce — do conteúdo — e o segmento `SEMCASO` declara isso em vez de
    esconder.
    """
    item = evento['ITEM_ID'].split('-', 1)[1]
    chave = chave_local(evento) or 'SEMCASO'
    base = f"{evento['ITEM_ID']}|{chave}|{texto_canonico(evento.get('REASON'))}"
    h = hashlib.sha1(base.encode('utf-8')).hexdigest()[:8].upper()
    return f'CLAIM-{item}-{chave}-{h}', None


ESQUEMAS = {'A_estrutural': esquema_A_estrutural,
            'B_conteudo': esquema_B_conteudo,
            'C_hibrido': esquema_C_hibrido}


def avaliar(esquema, claims):
    """Mede o comportamento do esquema sobre os claims reais + dois contraexemplos."""
    novo = collections.defaultdict(set)     # id novo -> textos canônicos distintos
    sem_chave = 0
    for evs in claims.values():
        for e in evs:
            cid, erro = esquema(e)
            if erro == 'SEM_CHAVE_LOCAL':
                sem_chave += 1
                continue
            novo[cid].add(texto_canonico(e.get('REASON')))
    colisoes = {k: v for k, v in novo.items() if len(v) > 1}

    # contraexemplo 1 · a MESMA afirmação reaparece → id tem de ser ESTÁVEL
    a = {'ITEM_ID': 'ITEM-AAAA', 'REASON': 'CASE-005 — a mesma frase', 'EVIDENCE_REFERENCE': 'CASE-005'}
    b = dict(a)
    estavel = esquema(a)[0] == esquema(b)[0]

    # contraexemplo 2 · MESMA chave local, texto DIFERENTE → tem de dar ids diferentes
    c = {'ITEM_ID': 'ITEM-AAAA', 'REASON': 'CASE-005 — França, colapso 2024', 'EVIDENCE_REFERENCE': 'CASE-005'}
    d = {'ITEM_ID': 'ITEM-AAAA', 'REASON': 'CASE-005 — Espanha, seca 2023', 'EVIDENCE_REFERENCE': 'CASE-005'}
    separa_texto = esquema(c)[0] != esquema(d)[0]

    # contraexemplo 3 · mesmo texto em ITENS diferentes → duas afirmações, dois ids
    e1 = {'ITEM_ID': 'ITEM-AAAA', 'REASON': 'CASE-009 — igual', 'EVIDENCE_REFERENCE': 'CASE-009'}
    e2 = {'ITEM_ID': 'ITEM-BBBB', 'REASON': 'CASE-009 — igual', 'EVIDENCE_REFERENCE': 'CASE-009'}
    separa_item = esquema(e1)[0] != esquema(e2)[0]

    # contraexemplo 4 · CUSTO declarado — correção de digitação muda o id?
    # Não é defeito nem virtude: é a moeda de troca entre legibilidade e content-address,
    # e ela tem de aparecer na tabela em vez de ser descoberta em produção.
    t1 = {'ITEM_ID': 'ITEM-AAAA', 'REASON': 'CASE-005 — a safra francesa de 2024',
          'EVIDENCE_REFERENCE': 'CASE-005'}
    t2 = {'ITEM_ID': 'ITEM-AAAA', 'REASON': 'CASE-005 — a safra francesa de 2024.',
          'EVIDENCE_REFERENCE': 'CASE-005'}
    sobrevive_typo = esquema(t1)[0] == esquema(t2)[0]

    return {
        'IDS_GERADOS': len(novo),
        'COLISOES_RESTANTES': len(colisoes),
        'CLAIMS_SEM_ID': sem_chave,
        'ESTAVEL_QUANDO_REPETE': estavel,
        'SEPARA_TEXTOS_DIFERENTES': separa_texto,
        'SEPARA_ITENS_DIFERENTES': separa_item,
        'SOBREVIVE_A_CORRECAO_DE_TEXTO': sobrevive_typo,
        'EXEMPLOS_DE_COLISAO': list(colisoes)[:3],
    }


# ── §3 · A PROPOSTA DE REEMISSÃO ───────────────────────────────────────────────────

def propor(eventos, claims, dependentes, esquema):
    """Mapa CLAIM_ID antigo -> novo, e o que NÃO pode ser reatribuído.

    Uma rota só é reatribuída quando ela declara a própria chave local. Rota órfã
    dentro de um id colidido fica `NAO_REATRIBUIVEL` — e isso é resultado, não falha:
    a informação de a qual afirmação ela pertencia não foi gravada.
    """
    mapa, nao_reatribuivel, sem_id = [], [], []

    # Índice (ITEM_ID, chave local) -> id NOVO do claim. Uma rota nunca reconstrói o
    # id por conta própria: ela procura o claim ao qual pertence. Reconstruir daria um
    # id parecido e inexistente — foi exatamente esse o defeito que o teste pegou.
    indice = {}
    for cid, evs in sorted(claims.items()):
        for e in evs:
            novo, erro = esquema(e)
            if erro:
                sem_id.append({'CLAIM_ID_ANTIGO': cid, 'EVENT_ID': e['EVENT_ID'],
                               'MOTIVO': erro})
                continue
            indice.setdefault((e['ITEM_ID'], chave_local(e)), novo)
            mapa.append({'CLAIM_ID_ANTIGO': cid, 'CLAIM_ID_NOVO': novo,
                         'EVENT_ID': e['EVENT_ID'], 'ITEM_ID': e['ITEM_ID'],
                         'CASO': chave_local(e),
                         'TEXTO': str(e.get('REASON'))[:120]})

    for cid, evs in sorted(claims.items()):
        ambiguo = len({texto_canonico(x.get('REASON')) for x in evs}) > 1
        for r in dependentes.get(cid, []):
            chave = chave_local(r)
            alvo = indice.get((r['ITEM_ID'], chave)) if chave else None
            if alvo:
                mapa.append({'CLAIM_ID_ANTIGO': cid, 'CLAIM_ID_NOVO': alvo,
                             'EVENT_ID': r['EVENT_ID'], 'ITEM_ID': r['ITEM_ID'],
                             'CASO': chave, 'TEXTO': f"[{r['EVENT_TYPE']}]"})
            elif chave:
                nao_reatribuivel.append({
                    'CLAIM_ID_ANTIGO': cid, 'EVENT_ID': r['EVENT_ID'],
                    'EVENT_TYPE': r['EVENT_TYPE'],
                    'CAPABILITY_ID': r.get('CAPABILITY_ID'),
                    'MOTIVO': f'a rota declara {chave}, e nenhum claim deste item foi '
                              f'extraído sob essa chave — a rota aponta para o vazio'})
            elif ambiguo:
                nao_reatribuivel.append({
                    'CLAIM_ID_ANTIGO': cid, 'EVENT_ID': r['EVENT_ID'],
                    'EVENT_TYPE': r['EVENT_TYPE'],
                    'CAPABILITY_ID': r.get('CAPABILITY_ID'),
                    'MOTIVO': 'rota sem chave local dentro de CLAIM_ID ambíguo — '
                              'a qual afirmação ela pertencia não foi gravado'})
            else:
                unico, _ = esquema(evs[0])
                mapa.append({'CLAIM_ID_ANTIGO': cid, 'CLAIM_ID_NOVO': unico,
                             'EVENT_ID': r['EVENT_ID'], 'ITEM_ID': r['ITEM_ID'],
                             'CASO': chave_local(evs[0]), 'TEXTO': f"[{r['EVENT_TYPE']}]"})
    return mapa, nao_reatribuivel, sem_id


# ── saída ──────────────────────────────────────────────────────────────────────────

# ── DRY-RUN · a tabela completa e a simulação do estado pós-reemissão ─────────────

def dry_run(eventos, claims, dependentes, esquema):
    """Tabela linha a linha + o stream de eventos SIMULADO. Nada é escrito.

    A simulação respeita append-only: os eventos antigos entram **intactos**, e a
    reemissão é um conjunto de eventos NOVOS que declaram `OLD_CLAIM_ID → CLAIM_ID`.
    O estado proposto é o que um consumidor derivaria depois de dobrar os dois.
    """
    mapa, orfas, sem_id = propor(eventos, claims, dependentes, esquema)
    por_evento = {m['EVENT_ID']: m['CLAIM_ID_NOVO'] for m in mapa}
    orfaos_evento = {o['EVENT_ID']: o['MOTIVO'] for o in orfas}

    # ---- a tabela pedida, uma linha por AFIRMAÇÃO real -----------------------------
    tabela = []
    for cid, evs in sorted(claims.items()):
        for e in evs:
            novo = por_evento.get(e['EVENT_ID'])
            caso = chave_local(e)
            rotas = [r for r in dependentes.get(cid, [])]
            direct = [r for r in rotas
                      if r.get('RELEVANCE') == 'DIRECT' and por_evento.get(r['EVENT_ID']) == novo]
            consumo = [r for r in rotas
                       if r.get('EVENT_TYPE') == 'CONSUMED_BY_CAPABILITY'
                       and por_evento.get(r['EVENT_ID']) == novo]
            bloq_rec = [r for r in rotas
                        if r.get('RELEVANCE') == 'BLOCKED' and por_evento.get(r['EVENT_ID']) == novo]
            bloq_orf = [r for r in rotas
                        if r.get('RELEVANCE') == 'BLOCKED' and r['EVENT_ID'] in orfaos_evento]
            tabela.append({
                'OLD_CLAIM_ID': cid,
                'NEW_CLAIM_ID': novo,
                'CASE_ID': caso,
                'CLAIM_TEXT': str(e.get('REASON'))[:150],
                'EVIDENCE_REFERENCE': e.get('EVIDENCE_REFERENCE'),
                'ITEM_ID': e['ITEM_ID'],
                'SOURCE_EVENT_ID': e['EVENT_ID'],
                'ROUTES_DIRECT_RECOVERED': len(direct),
                'ROUTES_CONSUMED_RECOVERED': len(consumo),
                'ROUTES_BLOCKED_RECOVERED': len(bloq_rec),
                # COMPARTILHADO entre as linhas do mesmo OLD_CLAIM_ID: se o id antigo
                # tinha 2 órfãs e 2 afirmações, as duas linhas mostram 2 — porque as
                # órfãs poderiam pertencer a qualquer uma. Somar a coluna conta duas
                # vezes de propósito; o total honesto está em PROVAS.ORPHANED_ROUTES.
                'ROUTES_UNRECOVERABLE_SHARED': len(bloq_orf) if len(evs) > 1 else 0,
                'REASON': ('id antigo carregava %d afirmações; a chave local %s separa'
                           % (len(evs), caso)) if len(evs) > 1
                          else 'id antigo já era único; reemitido para uniformizar a regra',
            })

    # ---- prova das rotas ----------------------------------------------------------
    direct_total = [r for r in eventos
                    if r.get('EVENT_TYPE') == 'ROUTED_TO_CAPABILITY'
                    and r.get('RELEVANCE') == 'DIRECT']
    direct_recuperadas, direct_erradas = [], []
    ids_de_claim = {m['CLAIM_ID_NOVO'] for m in mapa
                    if not str(m['TEXTO']).startswith('[')}
    for r in direct_total:
        novo = por_evento.get(r['EVENT_ID'])
        if novo is None:
            continue
        caso_da_rota = chave_local(r)
        # a rota está CERTA quando o id novo que ela recebeu contém o caso que ela declara
        if caso_da_rota and caso_da_rota in str(novo):
            direct_recuperadas.append(r['EVENT_ID'])
        else:
            direct_erradas.append({'EVENT_ID': r['EVENT_ID'], 'CASO_DA_ROTA': caso_da_rota,
                                   'NEW_CLAIM_ID': novo})

    rotas_para_claim_inexistente = sorted(
        {m['CLAIM_ID_NOVO'] for m in mapa if str(m['TEXTO']).startswith('[')} - ids_de_claim)

    # ---- o stream SIMULADO: antigos intactos + reemissão como eventos NOVOS --------
    novos_eventos = []
    for m in mapa:
        novos_eventos.append({
            'EVENT_TYPE': 'CLAIM_ID_REISSUED',
            'RULE_VERSION': RULE_VERSION,
            'ACTOR': 'scripts/passaporte_claim_id.py',
            'ITEM_ID': m['ITEM_ID'],
            'OLD_CLAIM_ID': m['CLAIM_ID_ANTIGO'],
            'CLAIM_ID': m['CLAIM_ID_NOVO'],
            'TARGET_EVENT_ID': m['EVENT_ID'],
            'REASON': 'identidade derivada de ordinal; reemitida a partir do conteúdo',
        })
    for o in orfas:
        novos_eventos.append({
            'EVENT_TYPE': 'CLAIM_LINK_ORPHANED',
            'RULE_VERSION': RULE_VERSION,
            'ACTOR': 'scripts/passaporte_claim_id.py',
            'OLD_CLAIM_ID': o['CLAIM_ID_ANTIGO'],
            'CLAIM_ID': None,
            'TARGET_EVENT_ID': o['EVENT_ID'],
            'CAPABILITY_ID': o.get('CAPABILITY_ID'),
            'TO_STATE': 'ORPHANED',
            'REASON': o['MOTIVO'],
        })

    # ---- o estado PROPOSTO, derivado da dobra ------------------------------------
    proposto = []
    for e in eventos:
        novo = por_evento.get(e['EVENT_ID'])
        if e['EVENT_ID'] in orfaos_evento:
            proposto.append(dict(e, CLAIM_ID=None, CLAIM_LINK_STATE='ORPHANED'))
        elif novo:
            proposto.append(dict(e, CLAIM_ID=novo))
        else:
            proposto.append(dict(e))

    # ---- COLLISIONS_AFTER: o gate rodado sobre o estado proposto ------------------
    depois = collections.defaultdict(set)
    for e in proposto:
        if e.get('EVENT_TYPE') == EV_CLAIM and e.get('CLAIM_ID'):
            depois[e['CLAIM_ID']].add(texto_canonico(e.get('REASON')))
    colisoes_depois = {k: v for k, v in depois.items() if len(v) > 1}

    return {
        'TABELA': tabela,
        'MAPA': mapa,
        'ORFAS': orfas,
        'SEM_CHAVE_LOCAL': sem_id,
        'EVENTOS_NOVOS': novos_eventos,
        'ESTADO_PROPOSTO': proposto,
        'PROVAS': {
            'CLAIMS_REAL': sum(len(v) for v in claims.values()),
            'NEW_CLAIM_IDS': len(ids_de_claim),
            'COLLISIONS_AFTER': len(colisoes_depois),
            'COLLISIONS_AFTER_DETALHE': sorted(colisoes_depois)[:3],
            'DIRECT_ROUTES_TOTAL': len(direct_total),
            'DIRECT_ROUTES_RECOVERED': len(direct_recuperadas),
            'DIRECT_ROUTES_WRONG': len(direct_erradas),
            'DIRECT_ROUTES_WRONG_DETALHE': direct_erradas[:5],
            'ROUTES_POINTING_TO_MISSING_CLAIM': len(rotas_para_claim_inexistente),
            'ORPHANED_ROUTES': len(orfas),
            'EVENTS_TO_APPEND': len(novos_eventos),
            'CLAIMS_REISSUED': sum(1 for m in mapa if not str(m['TEXTO']).startswith('[')),
            'ROUTES_REISSUED': sum(1 for m in mapa if str(m['TEXTO']).startswith('[')),
            'OLD_EVENTS_MODIFIED': 0,
        },
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('comando', choices=['medir', 'comparar', 'propor', 'dry-run'])
    p.add_argument('--passaporte', required=True)
    p.add_argument('--esquema', default='C_hibrido', choices=list(ESQUEMAS))
    p.add_argument('--json', default=None)
    p.add_argument('--simulado', default=None,
                   help='grava o estado proposto como JSONL de SIMULAÇÃO (nunca o log canônico)')
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    eventos = ler_eventos(args.passaporte)
    casos = ler_casos(args.passaporte)
    linhas, claims, dependentes = medir(eventos, casos)
    r = resumo(linhas)

    if args.comando == 'medir':
        print(f'RULE_VERSION = {RULE_VERSION}   ·   somente leitura')
        print(f'eventos lidos = {len(eventos)}   ·   casos declarados = {len(casos)}\n')
        for k, v in r.items():
            print(f'  {k:38s} = {v}')
        print('\n── TABELA DE COLISÕES ──')
        for l in linhas:
            if l['CLASSE'] == 'SEM_COLISAO':
                continue
            print(f"\n{l['CLAIM_ID']}   [{l['CLASSE']}]")
            print(f"   claims={l['N_CLAIMS']} · textos distintos={l['N_TEXTOS_DISTINTOS']}"
                  f" · rotas={l['N_ROTAS']} (órfãs={l['N_ROTAS_ORFAS']})")
            print(f"   ITEM_ID   : {', '.join(l['ITEM_IDS'])}")
            print(f"   casos     : {', '.join(l['CASOS']) or 'NENHUM'}")
            print(f"   capacidades: {', '.join(l['CAPACIDADES']) or 'nenhuma'}")
            if l['DIVERGENCIA_DE_CONTEXTO']:
                for eixo, vals in l['DIVERGENCIA_DE_CONTEXTO'].items():
                    print(f"   ⚠ {eixo} DIVERGE: {' ≠ '.join(v[:40] for v in vals)}")
            for t in l['TEXTOS']:
                print(f"     · {t}")

    elif args.comando == 'comparar':
        print(f'COMPARAÇÃO DE ESQUEMAS sobre {r["CLAIMS_TOTAL"]} claims reais\n')
        print(f'  {"esquema":16s} {"ids":>5s} {"colis":>6s} {"semid":>6s} '
              f'{"estável":>8s} {"sep.txt":>8s} {"sep.item":>9s} {"typo-ok":>8s}')
        for nome, fn in ESQUEMAS.items():
            a = avaliar(fn, claims)
            print(f'  {nome:16s} {a["IDS_GERADOS"]:5d} {a["COLISOES_RESTANTES"]:6d} '
                  f'{a["CLAIMS_SEM_ID"]:6d} {str(a["ESTAVEL_QUANDO_REPETE"]):>8s} '
                  f'{str(a["SEPARA_TEXTOS_DIFERENTES"]):>8s} '
                  f'{str(a["SEPARA_ITENS_DIFERENTES"]):>9s} '
                  f'{str(a["SOBREVIVE_A_CORRECAO_DE_TEXTO"]):>8s}')
            if a['EXEMPLOS_DE_COLISAO']:
                print(f'      colisões restantes: {a["EXEMPLOS_DE_COLISAO"]}')
        print('\n  sep.txt = separa dois textos diferentes sob a MESMA chave local')
        print('  typo-ok = o id SOBREVIVE a uma correção de digitação no texto')
        print('  Nenhum esquema tem os dois: separar por conteúdo é, por definição,')
        print('  mudar de id quando o conteúdo muda. A escolha é qual erro se prefere.')
        print('\n  Exemplos de id gerado para o caso-testemunha:')
        alvo = [e for evs in claims.values() for e in evs
                if chave_local(e) in ('CASE-005', 'CASE-006')
                and e['ITEM_ID'] == 'ITEM-3CA2E441A6D5FD7A']
        for nome, fn in ESQUEMAS.items():
            ids = [fn(e)[0] for e in alvo]
            print(f'    {nome:16s} {" | ".join(str(i) for i in ids)}')

    elif args.comando == 'dry-run':
        d = dry_run(eventos, claims, dependentes, ESQUEMAS[args.esquema])
        pr = d['PROVAS']
        print(f'DRY-RUN · esquema={args.esquema} · {RULE_VERSION}')
        print('NADA FOI ESCRITO. EVENTOS.jsonl intacto.\n')
        print('── PROVAS ──')
        for k, v in pr.items():
            if k.endswith('_DETALHE'):
                continue
            print(f'  {k:38s} = {v}')
        if pr['DIRECT_ROUTES_WRONG']:
            print('  DIRECT ERRADAS:', pr['DIRECT_ROUTES_WRONG_DETALHE'])

        print('\n── TABELA (as 12 colisões; uma linha por afirmação) ──')
        colididos = {l['OLD_CLAIM_ID'] for l in d['TABELA']
                     if sum(1 for x in d['TABELA'] if x['OLD_CLAIM_ID'] == l['OLD_CLAIM_ID']) > 1}
        for l in d['TABELA']:
            if l['OLD_CLAIM_ID'] not in colididos:
                continue
            print(f"\n  OLD  {l['OLD_CLAIM_ID']}")
            print(f"  NEW  {l['NEW_CLAIM_ID']}")
            print(f"       CASE={l['CASE_ID']}  ·  DIRECT={l['ROUTES_DIRECT_RECOVERED']}"
                  f"  CONSUMED={l['ROUTES_CONSUMED_RECOVERED']}"
                  f"  BLOCKED_REC={l['ROUTES_BLOCKED_RECOVERED']}"
                  f"  UNRECOVERABLE_SHARED={l['ROUTES_UNRECOVERABLE_SHARED']}")
            print(f"       {l['CLAIM_TEXT'][:100]}")

        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump({'RULE_VERSION': RULE_VERSION, 'ESQUEMA': args.esquema,
                           'PROVAS': pr, 'TABELA': d['TABELA'],
                           'EVENTOS_A_ACRESCENTAR': d['EVENTOS_NOVOS'],
                           'ORFAS': d['ORFAS']},
                          f, ensure_ascii=False, indent=2)
            print(f'\npreview gravado: {args.json}  (proposta — nada aplicado)')
        if args.simulado:
            # Artefato de SIMULAÇÃO. Não é o log canônico e não pode virar um.
            # Fica fora de data/passaporte/ de propósito.
            os.makedirs(os.path.dirname(os.path.abspath(args.simulado)), exist_ok=True)
            with open(args.simulado, 'w', encoding='utf-8') as f:
                for e in d['ESTADO_PROPOSTO']:
                    f.write(json.dumps(e, ensure_ascii=False) + '\n')
            print(f'estado simulado gravado: {args.simulado}')
            print('  ATENÇÃO: simulação. NÃO é data/passaporte/EVENTOS.jsonl.')
        return 0

    else:
        mapa, orfas, sem_id = propor(eventos, claims, dependentes, ESQUEMAS[args.esquema])
        novos = {m['CLAIM_ID_NOVO'] for m in mapa}
        print(f'PROPOSTA DE REEMISSÃO · esquema={args.esquema} · RULE_VERSION={RULE_VERSION}')
        print(f'  eventos remapeados          = {len(mapa)}')
        print(f'  CLAIM_ID antigos            = {r["CLAIM_IDS_TOTAL"]}')
        print(f'  CLAIM_ID novos              = {len(novos)}')
        print(f'  rotas NAO_REATRIBUIVEIS     = {len(orfas)}')
        print(f'  claims sem chave local      = {len(sem_id)}')
        if orfas:
            print('\n  ── o que NÃO pode ser reatribuído (a informação não foi gravada) ──')
            for o in orfas[:10]:
                print(f"     {o['CLAIM_ID_ANTIGO']} · {o['EVENT_TYPE']} · "
                      f"{o['CAPABILITY_ID']} · {o['EVENT_ID']}")
        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump({'RULE_VERSION': RULE_VERSION, 'ESQUEMA': args.esquema,
                           'RESUMO': r, 'MAPA': mapa,
                           'NAO_REATRIBUIVEL': orfas, 'SEM_CHAVE_LOCAL': sem_id},
                          f, ensure_ascii=False, indent=2)
            print(f'\ngravado: {args.json}   (proposta — nada foi aplicado ao log)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
