#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A AUDITORIA DA ESPÉCIE — o que se SUSPEITA, ao lado do que se SABE.

    py provas/especie_do_texto_auditoria.py            # a tabela
    py provas/especie_do_texto_auditoria.py --gravar   # o artefato derivado

O QUE ISTO É, E O QUE NÃO PODE VIRAR
--------------------------------------
A C5 leu os 28 textos pagos e viu onze em inglês vindos de vídeo não-inglês. Isso
é uma observação verdadeira e útil. **Não é** a espécie canônica daqueles textos.

    AUDIT_CLASSIFICATION != TRANSCRIPT_KIND.

A lei que a própria C5 escreveu diz que a espécie vem do PROVEDOR, nunca de
inferência sobre o conteúdo. Se esta auditoria alimentasse `TRANSCRIPT_KIND`, ela
revogaria a lei que a tornou possível — e o corpus passaria a carregar como facto
aquilo que é leitura nossa.

```
QUEM INFERE PODE SUSPEITAR. QUEM INFERE NÃO PODE CARIMBAR.
```

Por isso os campos daqui têm prefixo `AUDIT_`, o canônico sai sempre `NOT_KNOWN`,
e há prova que reprova se alguém ligar um ao outro.

O QUE ISTO NÃO FAZ
-------------------
Não edita os artefatos históricos. Não traduz nada de volta. Não completa idioma.
O que ficou gravado em 2026-09 continua a dizer o que a casa sabia em 2026-09 —

    HISTORICAL_EVIDENCE != REWRITTEN_HISTORY.

E não decide se o texto presta: relevância, sinal e verdade são de outra camada.
Aqui só se pergunta de onde o texto veio.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                      # noqa: E402,F401
import proveniencia as pv            # noqa: E402

PILOTO = os.path.join(RAIZ, 'data', 'samples', 'SENSOR-PILOT')
LOTES = ('A', 'B', 'C', 'D', 'E')
SAIDA = os.path.join(PILOTO, 'ESPECIE-DO-TEXTO-AUDITORIA-V1.json')

SUSPEITO = 'YES'
NAO_SUSPEITO = 'NO'
INDETERMINADO = 'UNKNOWN'

# ── AS PALAVRAS FUNCIONAIS, E POR QUE SÃO ELAS ──────────────────────────────
# Palavra funcional — artigo, preposição, conjunção — é o sinal de língua mais
# barato e mais honesto que existe: ela não fala do assunto, fala da gramática.
# Um texto agronómico italiano e um espanhol partilham «fusariosi/fusariosis»;
# não partilham «della» e «para».
#
# E isto NÃO é um detector de língua sério. É uma peneira declarada, com o seu
# limite escrito ao lado: abaixo de três marcadores devolve `UNKNOWN`, e empate
# devolve `UNKNOWN`. Uma peneira que confessa o buraco vale mais do que um
# detector que não o confessa.
MARCAS = {
    'it': re.compile(r'\b(della|delle|nella|degli|questo|questa|perche|anche|'
                     r'sono|come|piu|gli|nel|con|che|non|per)\b'),
    'es': re.compile(r'\b(para|como|pero|este|esta|muy|hay|son|mas|los|las|del|'
                     r'que|con|una)\b'),
    'fr': re.compile(r'\b(pour|avec|dans|cette|comme|sont|plus|nous|vous|est|'
                     r'les|des|une|que)\b'),
    'en': re.compile(r'\b(the|and|for|with|that|this|from|have|are|you|your|'
                     r'about|will|been|were)\b'),
}
PISO_DE_MARCADORES = 3


def _lingua(texto):
    """→ (língua, evidência). Empate ou pouco sinal = UNKNOWN, nunca chute."""
    t = (texto or '').lower()
    pont = {k: len(v.findall(t)) for k, v in MARCAS.items()}
    top = sorted(pont.items(), key=lambda kv: -kv[1])
    if not top or top[0][1] < PISO_DE_MARCADORES:
        return INDETERMINADO, 'menos de %d marcadores funcionais' % PISO_DE_MARCADORES
    if len(top) > 1 and top[0][1] == top[1][1]:
        return INDETERMINADO, 'empate entre %s e %s' % (top[0][0], top[1][0])
    return top[0][0], '%d marcadores de %s' % (top[0][1], top[0][0])


def _metadados():
    """Título e descrição por vídeo, do que já está preservado."""
    fora = {}
    for L in LOTES:
        p = os.path.join(PILOTO, 'VIDEOS-%s.json' % L)
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as f:
            for i in json.load(f).get('ITEMS') or []:
                vid = str(i.get('EXTERNAL_ID') or '')
                if vid:
                    fora[vid] = i
    return fora


def _transcricoes():
    """Os textos, com a espécie que o REGISTO carrega (não a que eu acho)."""
    fora, pais = [], []
    for L in LOTES:
        p = os.path.join(PILOTO, 'TRANSCRICOES-%s.json' % L)
        if not os.path.exists(p):
            continue
        pais.append(os.path.relpath(p, RAIZ).replace('\\', '/'))
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        for i in d.get('ITEMS') or []:
            m = re.search(r'v=([\w-]{6,})', str(i.get('SOURCE_URL') or ''))
            fora.append({
                'VIDEO_ID': m.group(1) if m else pv.NAO_SEI,
                'SOURCE_URL': i.get('SOURCE_URL'),
                'TRANSCRIPT': i.get('TRANSCRIPT'),
                'KIND_NO_REGISTO': i.get('TRANSCRIPT_KIND') or pv.NAO_SEI,
                'CAPTION_SOURCE': i.get('CAPTION_SOURCE'),
                'PARENT_ARTIFACT': os.path.relpath(p, RAIZ).replace('\\', '/'),
            })
    return fora, pais


def auditar():
    meta = _metadados()
    itens, pais = _transcricoes()
    linhas = []
    for it in itens:
        v = meta.get(it['VIDEO_ID']) or {}
        fonte = '%s %s' % (v.get('TITLE') or '', (v.get('DESCRIPTION') or '')[:600])
        lf, ef = _lingua(fonte)
        lt, et = _lingua(it['TRANSCRIPT'] or '')

        # SUSPEITA, e ela tem três estados porque a ausência de sinal não é
        # ausência de tradução. Sem língua de um dos lados, não se afirma nada.
        if not it['TRANSCRIPT']:
            suspeita, porque = INDETERMINADO, 'sem texto para comparar'
        elif lf == INDETERMINADO or lt == INDETERMINADO:
            suspeita, porque = INDETERMINADO, 'sinal de lingua insuficiente (%s | %s)' % (ef, et)
        elif lf != lt:
            suspeita, porque = SUSPEITO, 'fonte parece %s e o texto parece %s' % (lf, lt)
        else:
            suspeita, porque = NAO_SUSPEITO, 'fonte e texto parecem %s' % lf

        linhas.append({
            'ITEM_ID': it['VIDEO_ID'],
            'SOURCE_URL': it['SOURCE_URL'],
            'PARENT_ARTIFACT': it['PARENT_ARTIFACT'],
            'SOURCE_TITLE': v.get('TITLE') or pv.NAO_SEI,
            # ── O CANÔNICO, E ELE NÃO SE MEXE ────────────────────────────
            # Sai do registo, e o registo histórico não declara espécie. Esta
            # auditoria NUNCA o altera — nem quando tem a certeza.
            'TRANSCRIPT_KIND_CANONICAL': it['KIND_NO_REGISTO'],
            'CANONICAL_BASIS': pv.NOT_DECLARED,
            # ── O OBSERVADO, com prefixo próprio para nunca se confundir ──
            'AUDIT_SOURCE_LANGUAGE_SIGNAL': lf,
            'AUDIT_TEXT_LANGUAGE_SIGNAL': lt,
            'AUDIT_TRANSLATION_SUSPECT': suspeita,
            'AUDIT_BASIS': porque,
            'AUDIT_METHOD': 'palavra funcional sobre titulo+descricao vs texto; '
                            'piso de %d marcadores; empate = UNKNOWN' % PISO_DE_MARCADORES,
        })
    return linhas, pais


def corpo():
    linhas, pais = auditar()
    com_texto = [x for x in linhas if x['AUDIT_TRANSLATION_SUSPECT'] != INDETERMINADO
                 or x['AUDIT_BASIS'] != 'sem texto para comparar']
    conta = {e: sum(1 for x in linhas if x['AUDIT_TRANSLATION_SUSPECT'] == e)
             for e in (SUSPEITO, NAO_SUSPEITO, INDETERMINADO)}
    return {
        'SOURCE_ID': 'SENSOR-PILOT/ESPECIE-DO-TEXTO-AUDITORIA-V1',
        'ARTIFACT_KIND': 'DERIVED',
        'PARENT_ARTIFACTS': pais,
        'source': 'leitura DERIVADA dos artefatos de transcricao ja preservados',
        'SOURCE_LOCATION': 'derivado — nenhuma coleta nova',
        'EVIDENCE_CLASS': 'DERIVED_AUDIT',
        # A HORA EM QUE ESTA LEITURA FOI FEITA — e nao a da coleta. Uma
        # auditoria que herdasse a data do pai diria que observou em 2026-09-02
        # uma coisa que so foi observada hoje.
        'CAPTURED_AT': datetime.datetime.now(datetime.timezone.utc)
                               .strftime('%Y-%m-%dT%H:%M:%SZ'),
        'APIFY_RUNS': 0,
        'COST_USD': 0,
        'LEI': ('AUDIT_CLASSIFICATION != TRANSCRIPT_KIND. Os campos AUDIT_* sao '
                'LEITURA sobre o conteudo; o campo canonico vem do provedor e '
                'continua NAO SEI. Nada aqui alimenta o contrato de procedencia.'),
        'O_QUE_ISTO_NAO_E': ('nao e a especie dos textos, nao e juizo de qualidade, '
                             'nao e relevancia, e nao substitui o registo historico'),
        'COUNTS': dict(conta, ITEMS=len(linhas), COM_TEXTO=len(com_texto)),
        'ITEMS': linhas,
    }


def main():
    d = corpo()
    if '--gravar' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print('gravado em %s' % os.path.relpath(SAIDA, RAIZ))
        return 0
    print('\nAUDITORIA DA ESPECIE DO TEXTO — leitura, nunca carimbo')
    print('=' * 96)
    print('  %-13s %-6s %-6s %-9s %s' % ('VIDEO', 'FONTE', 'TEXTO', 'SUSPEITA', 'TITULO'))
    print('  ' + '-' * 92)
    for x in d['ITEMS']:
        if not x['SOURCE_TITLE'] or x['AUDIT_BASIS'] == 'sem texto para comparar':
            continue
        print('  %-13s %-6s %-6s %-9s %s'
              % (x['ITEM_ID'][:13], x['AUDIT_SOURCE_LANGUAGE_SIGNAL'],
                 x['AUDIT_TEXT_LANGUAGE_SIGNAL'], x['AUDIT_TRANSLATION_SUSPECT'],
                 str(x['SOURCE_TITLE'])[:42]))
    print('\n  CONTAGEM  %s' % d['COUNTS'])
    canon = {x['TRANSCRIPT_KIND_CANONICAL'] for x in d['ITEMS']}
    print('  ESPECIE CANONICA de todos os itens: %s' % (canon or '—'))
    print('  (e continua assim: o provedor nunca declarou, e auditoria nao carimba)')
    print('')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
