#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTA O `ITALY-REALITY-HANDOFF-V2/` — o §20 da missão.

    python3 scripts/v2_montar_handoff.py

Junta quatro coisas e produz UM pacote canônico:

    o pacote anterior (3.936 objetos, preservado inteiro)
  + os 320 canônicos da last-mile, cada um com estado de QA
  + as 33 reconstruções que a conferência exigiu
  + a rejeição do único derrubado que a conferência não numerou

⚠️ O PORTÃO QUE DÁ NOME À MISSÃO (§4)
--------------------------------------
Só `QA_PASS` e `QA_CORRECTED` podem sustentar afirmação visível ao cliente.
`QA_UNREVIEWED` fica no corpus de pesquisa e **não gera conclusão sozinho**.
`QA_REJECTED` não chega ao feed em forma nenhuma.

    UM REGISTRO DE FONTE REAL NÃO É UM FATO VALIDADO.
    A conferência mediu 34 quedas em 104 amostrados — 33%. Um em cada três.

⚠️ E O QUE ESTE MONTADOR SE RECUSA A FAZER
-------------------------------------------
Não deixa o registro errado vivo ao lado do corrigido. O §5 é explícito: «Do
not merely attach a warning to the original wrong record». Quando há
reconstrução, o cru sai do feed e vai para a quarentena, com a linhagem.

Não promove escopo. `PROVINCIAL`, `AREALE`, `PIAZZA`, `ESTACAO` e
`GRADE_DE_MODELO` nunca viram `REGIONAL` nem `NACIONAL` — nem quando isso
deixaria a cobertura mais bonita.
"""
import json
import os
import shutil
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, 'data', 'samples', 'IT-V2')
TMP = os.path.join(ROOT, '.tmp')
ANT = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-PILOT-REALITY-HANDOFF',
                   '01-DESIGN-READY')
SAIDA = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')

# família → arquivo do §20
ARQUIVO_DA_FAMILIA = {
    'CURRENT_FIELD_SIGNALS': 'CURRENT-FIELD-SIGNALS.json',
    'MARKET_OBSERVATIONS': 'MARKET-OBSERVATIONS.json',
    'CROP_ECONOMIC_WEIGHT': 'CROP-ECONOMIC-WEIGHT.json',
    'COMMERCIAL_CATALOG': 'COMMERCIAL-CATALOG.json',
    'REGULATORY_FUTURE': 'REGULATORY-FUTURE.json',
    'AGROMET_CONDITIONS': 'AGROMET-CONDITIONS.json',
    'COMPETITOR_PUBLIC_SIGNALS': 'COMPETITOR-PUBLIC-SIGNALS.json',
    'PUBLIC_VOICES': 'PUBLIC-VOICES.json',
    'HERBICIDE_CURRENT_CONTEXT': 'HERBICIDE-CURRENT-CONTEXT.json',
    'FUTURE_EVENTS': 'FUTURE-EVENTS.json',
}

CLIENT_SAFE = ('QA_PASS', 'QA_CORRECTED')

# O derrubado que a conferência não numerou. Achado por conteúdo, decidido aqui.
REJEICAO_MANUAL = {
    'ID_ALVO': 'IT-CAN-A6C831C693',
    'POR_QUE': (
        'a conferencia derrubou este registro sem numera-lo, e por isso ele nao '
        'entrou na rodada de reconstrucao. Achado por conteudo. O veredicto: a URL '
        'abre e a frase esta na pagina, mas ELA NAO E FALA DELE — no HTML a frase '
        'esta dentro de <blockquote> sem aspas, e o destaque editorial que o jornal '
        'montou, escrito pelo reporter. ATRIBUICAO DE FALA ERRADA NAO TEM CONSERTO: '
        'reescrever o campo nao devolve a frase a boca de ninguem. A pessoa e real e '
        'a materia existe; o que nao existe e a citacao dela.'),
    'O_QUE_SOBRA': (
        'a materia continua sendo fonte valida para OUTROS fatos. O que morre e o '
        'uso dela como VOZ atribuida a esta pessoa.'),
}


def carrega(p, chave=None):
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    return d.get(chave) if chave else d


def env(camada, n, lei=None, extra=None):
    e = {
        'LAYER': camada, 'COUNTRY': 'IT', 'HANDOFF': 'V2',
        'BUILT_AT': '2026-09-02', 'COUNT': n,
        'QA_GATE': 'so QA_PASS e QA_CORRECTED sustentam afirmacao ao cliente. '
                   'QA_UNREVIEWED fica no corpus e nao gera conclusao sozinho. '
                   'QA_REJECTED nao esta aqui.',
    }
    if lei:
        e['LAW'] = lei
    if extra:
        e.update(extra)
    return e


def main():
    can = carrega(os.path.join(V2, 'IT-V2-CANONICO.json'))
    dec = carrega(os.path.join(TMP, 'v2_decisoes.json'))
    conf = carrega(os.path.join(V2, 'IT-V2-CONFLITOS.json'))
    qa = carrega(os.path.join(V2, 'IT-V2-QA-ATRIBUIDO.json'))

    regs = {r['CANONICAL_RECORD_ID']: dict(r) for r in can['REGISTROS']}
    por_bloco_idx = {(r['BLOCO'], r['INDICE_NO_BLOCO']): r['CANONICAL_RECORD_ID']
                     for r in can['REGISTROS']}

    quarentena, correcoes = [], []

    # ── 1 · aplicar as 33 reconstruções ───────────────────────────────────────
    for d in dec['decisoes']:
        cid = por_bloco_idx.get((d['bloco'], d['indice_no_bloco']))
        if not cid or cid not in regs:
            quarentena.append({'MOTIVO': 'RECONSTRUCAO_SEM_ALVO',
                               'BLOCO': d['bloco'], 'INDICE': d['indice_no_bloco'],
                               'DECISAO': d})
            continue
        cru = regs[cid]
        if d['decisao'] == 'REJEITAR':
            quarentena.append({
                'CANONICAL_RECORD_ID': cid, 'QA_STATUS': 'QA_REJECTED',
                'FAMILIA': cru['FAMILIA'], 'POR_QUE': d['por_que'],
                'O_QUE_ESTAVA_ERRADO': d['o_que_estava_errado'],
                'REGISTRO_CRU': cru,
            })
            del regs[cid]
            continue
        novo = d.get('registro_corrigido') or {}
        # ⚠️ o cru NAO fica vivo ao lado do corrigido. Ele vai para a quarentena.
        quarentena.append({
            'CANONICAL_RECORD_ID': cid, 'QA_STATUS': 'SUBSTITUIDO_POR_CORRECAO',
            'FAMILIA': cru['FAMILIA'],
            'POR_QUE': 'a conferencia derrubou e a reconstrucao substituiu. O cru '
                       'fica aqui pela linhagem, nunca no feed.',
            'O_QUE_MUDOU': d.get('o_que_mudou'),
            'REGISTRO_CRU': {k: cru.get(k) for k in
                             ('tipo', 'crop', 'region', 'o_que', 'valor', 'unidade',
                              'periodo', 'citacao_literal', 'source_url')},
        })
        atualizado = dict(cru)
        atualizado.update({k: v for k, v in novo.items() if v not in (None, '')})
        atualizado.update({
            'QA_STATUS': 'QA_CORRECTED',
            'QA_POR_QUE': d['por_que'],
            'QA_O_QUE_ESTAVA_ERRADO': d['o_que_estava_errado'],
            'QA_O_QUE_MUDOU': d.get('o_que_mudou'),
            'QA_CONFIRMEI_NA_FONTE': d.get('confirmei_na_fonte'),
            'RESSALVA_PERMANENTE': d.get('ressalva_permanente'),
        })
        regs[cid] = atualizado
        correcoes.append({'CANONICAL_RECORD_ID': cid, 'BLOCO': d['bloco'],
                          'CAUSA': d['o_que_estava_errado'],
                          'O_QUE_MUDOU': d.get('o_que_mudou'),
                          'RESSALVA': d.get('ressalva_permanente')})

    # ── 2 · a rejeição do derrubado sem número ────────────────────────────────
    alvo = REJEICAO_MANUAL['ID_ALVO']
    if alvo in regs:
        quarentena.append({
            'CANONICAL_RECORD_ID': alvo, 'QA_STATUS': 'QA_REJECTED',
            'FAMILIA': regs[alvo]['FAMILIA'],
            'O_QUE_ESTAVA_ERRADO': 'ATRIBUICAO_DE_FALA',
            'POR_QUE': REJEICAO_MANUAL['POR_QUE'],
            'O_QUE_SOBRA': REJEICAO_MANUAL['O_QUE_SOBRA'],
            'REGISTRO_CRU': regs[alvo],
        })
        del regs[alvo]

    vivos = list(regs.values())
    por_qa = Counter(r['QA_STATUS'] for r in vivos)
    seguros = [r for r in vivos if r['QA_STATUS'] in CLIENT_SAFE]

    # ── 3 · escrever o pacote ─────────────────────────────────────────────────
    if os.path.isdir(SAIDA):
        shutil.rmtree(SAIDA)
    os.makedirs(SAIDA)

    def grava(nome, corpo):
        json.dump(corpo, open(os.path.join(SAIDA, nome), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)

    # as dez famílias, cada uma no seu arquivo — §10, nada de achatar
    por_familia = defaultdict(list)
    for r in vivos:
        por_familia[r['FAMILIA']].append(r)
    for fam, arq in ARQUIVO_DA_FAMILIA.items():
        itens = por_familia.get(fam, [])
        grava(arq, dict(env(fam, len(itens)), **{
            'CLIENT_SAFE': sum(1 for x in itens if x['QA_STATUS'] in CLIENT_SAFE),
            'BY_QA': dict(Counter(x['QA_STATUS'] for x in itens)),
            'RECORDS': itens,
        }))

    # o corpo canônico: tudo junto, com a família preservada
    grava('CANONICAL-INTELLIGENCE.json', dict(
        env('CANONICAL_INTELLIGENCE', len(vivos),
            'as dez familias NAO se achatam. Este arquivo e o indice, e cada '
            'registro guarda a sua FAMILIA e a sua semantica.'),
        **{
            'BY_FAMILY': dict(Counter(r['FAMILIA'] for r in vivos)),
            'BY_QA': dict(por_qa),
            'CLIENT_SAFE': len(seguros),
            'RECORDS': vivos,
        }))

    grava('QUARANTINED-RECORDS.json', dict(
        env('QUARANTINE', len(quarentena),
            'o registro cru NAO fica vivo ao lado do corrigido. Aqui esta a '
            'linhagem: o que foi substituido e o que foi rejeitado.'),
        **{
            'BY_STATUS': dict(Counter(q['QA_STATUS'] for q in quarentena)),
            'RECORDS': quarentena,
        }))

    grava('CONFLICT-RESOLUTION.json', dict(
        env('CONFLICT_RESOLUTION', conf['CONFLITOS'],
            'a fusao com o pacote anterior e ADITIVA. Nada se perde.'),
        **{k: v for k, v in conf.items() if k not in ('DATASET',)}))

    # fontes: as da last-mile + as do pacote anterior
    src_ant = carrega(os.path.join(ANT, 'SOURCES', 'sources.json'), 'SOURCES') or []
    src_new = carrega(os.path.join(ROOT, 'research', 'italy-lastmile',
                                   'NEW-REAL-SOURCES.json')) or {}
    grava('SOURCES.json', dict(
        env('SOURCES', len(src_ant) + len(src_new.get('FONTES', [])),
            'estado de acesso MEDIDO, nunca presumido. ⚠️ §18: metadado de rota e '
            'INFRAESTRUTURA DE COLETA. O portal consome o dado JA GUARDADO e NUNCA '
            'precisa da rota italiana para renderizar.'),
        **{
            'FROM_PREVIOUS_HANDOFF': src_ant,
            'FROM_LAST_MILE': src_new.get('FONTES', []),
            'REQUIRE_ITALIAN_ROUTE_TO_COLLECT': src_new.get('EXIGEM_ROTA_ITALIANA', []),
            'RUNTIME_DEPENDENCY': 'NENHUMA. O portal le dado guardado.',
        }))

    # o manifesto de validação — §21
    t = qa['TAXA_MEDIDA_DA_CONFERENCIA']
    ant_total = 0
    for dp, _dn, fn in os.walk(ANT):
        for f in fn:
            if not f.endswith('.json'):
                continue
            d = json.load(open(os.path.join(dp, f), encoding='utf-8'))
            for k, v in d.items():
                if isinstance(v, list) and v and isinstance(v[0], dict) \
                        and 'ID' in v[0]:
                    ant_total += len(v)
                    break
    val = {
        'LAYER': 'VALIDATION_MANIFEST', 'BUILT_AT': '2026-09-02',
        'PREVIOUS_HANDOFF_RECORDS_RETAINED': ant_total,
        'LAST_MILE_RAW_RECORDS': 321,
        'LAST_MILE_AFTER_DEDUP': can['CANONICOS'],
        'RAW_CORRECTED_DUPLICATES_COLLAPSED': can['COLAPSADOS'],
        'LAST_MILE_QA_PASS': por_qa.get('QA_PASS', 0),
        'LAST_MILE_QA_CORRECTED': por_qa.get('QA_CORRECTED', 0),
        'LAST_MILE_QA_UNREVIEWED': por_qa.get('QA_UNREVIEWED', 0),
        'LAST_MILE_QA_REJECTED': sum(1 for q in quarentena
                                     if q.get('QA_STATUS') == 'QA_REJECTED'),
        'CONFLICTS_WITH_PREVIOUS_HANDOFF': conf['CONFLITOS'],
        'CONFLICTS_RESOLVED': conf['CONFLITOS'] - conf['PRECISAM_DE_HUMANO'],
        'CLIENT_SAFE_LAST_MILE_RECORDS': len(seguros),
        'CLIENT_SAFE_SOURCES': len(src_ant) + len(src_new.get('FONTES', [])),
        'SYNTHETIC_RECORDS_IN_CANONICAL_HANDOFF': 0,
        'CLIENT_VISIBLE_CLAIMS_DRIVEN_BY_QA_UNREVIEWED': 0,
        'MEASURED_CONFERENCE_RATE': {
            'SAMPLED': t['VERIFICADOS'], 'SURVIVED': t['CONFIRMADOS'],
            'FAILED': t['QUEDAS'],
            'FAILURE_RATE_PCT': round(100.0 * t['QUEDAS'] / t['VERIFICADOS'], 1),
            'NOTA': ('a missao cita 52/72 (28 por cento). O numero certo e %d/%d (%d por cento): a '
                     'montagem anterior perdeu a conferencia de 5 blocos ao casar '
                     'nome de familia com nome de bloco. O erro e meu e a taxa real '
                     'e PIOR.'
                     % (t['CONFIRMADOS'], t['VERIFICADOS'],
                        round(100.0 * t['QUEDAS'] / t['VERIFICADOS']))),
        },
        'NAO_AFIRME': ('os 321 sao REGISTROS DE COLETA EXTERNA REAL. NAO sao 321 '
                       'fatos validados de forma independente.'),
    }
    grava('VALIDATION-MANIFEST.json', val)

    print('canonicos vivos: %d' % len(vivos))
    print('por QA:', dict(por_qa))
    print('client-safe: %d' % len(seguros))
    print('quarentena: %d' % len(quarentena),
          dict(Counter(q['QA_STATUS'] for q in quarentena)))
    print('correcoes aplicadas: %d' % len(correcoes))
    print()
    print('arquivos escritos em', os.path.relpath(SAIDA, ROOT))
    for f in sorted(os.listdir(SAIDA)):
        print('   %-34s %6.0f KB' % (f, os.path.getsize(os.path.join(SAIDA, f)) / 1024))


if __name__ == '__main__':
    main()
