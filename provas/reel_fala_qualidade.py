#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«GEROU TEXTO» NÃO É APROVAÇÃO — a prova de que a fala escrita bate com a fala dita.

    py provas/reel_fala_qualidade.py             # mede sobre o corpus já transcrito
    py provas/reel_fala_qualidade.py comparar    # re-ouve com dois modelos e compara

O PROBLEMA QUE ISTO RESOLVE
-----------------------------
Um reconhecedor devolve sempre alguma coisa. Um lote inteiro pode sair com
`TRANSCRIPT_STATE = OK`, mil textos bonitos, e o corpus estar arruinado — porque
o que interessa a esta casa não é a frase: é o NOME DA CULTURA, o NOME DA MARCA
e o NOME DA DOENÇA. E é exatamente aí que o modelo barato falha.

Medido em 2026-09-10, no Reel real `C-FanW_CYMz` da @syngentaitalia:

    o que foi dito       `small` escreveu     `medium` escreveu
    ------------------   ------------------   ------------------
    mais                 MICE                 mais
    maiscoltori          mai scoltori         maiscoltori
    Discovery Seeds      Discovery Seats      Discovery Seeds
    eventi               venti                eventi

    A FRASE ESTAVA CERTA NAS DUAS. O SINAL SÓ ESTAVA NUMA.

Um corpus que existe para responder «de que cultura o concorrente fala?» não
sobrevive a «MICE». Não é uma imprecisão: é o sinal perdido, em silêncio, com o
texto a parecer normal.

O GABARITO, E DE ONDE ELE VEM
-------------------------------
Não há transcrição oficial destes Reels — logo não há como calcular uma taxa de
erro por palavra sem inventar o denominador. O que existe é uma âncora HONESTA:

    a LEGENDA, escrita pelo autor, nomeia a marca e muitas vezes a cultura.

Se a fala diz «Syngenta» e a legenda escreve «Syngenta», exigir que a
transcrição escreva «Syngenta» não é arbitrário — é conferir contra o próprio
autor. Cada termo esperado abaixo tem a sua ORIGEM declarada, e nenhum foi
escolhido por vir a calhar.

    O DENOMINADOR ESTÁ À VISTA: é o número de termos esperados por caso, e
    está impresso ao lado de cada resultado. Não há percentagem sem ele.

O QUE ISTO NÃO MEDE
---------------------
Não mede fluência, não mede pontuação, não mede se o texto «soa bem», e NÃO é
uma taxa de acerto por palavra. Um caso PASS quer dizer «os termos que importam
apareceram», não «a transcrição está perfeita».
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

CORPUS = os.path.join(ROOT, 'data', 'samples', 'REEL-TRANSCRICOES',
                      'TRANSCRICOES-REEL.json')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'REEL-TRANSCRICOES',
                     'QUALIDADE-DA-FALA-V1.json')

PASS, PARTIAL, FAIL = 'PASS', 'PARTIAL', 'FAIL'

# ── O QUE SE ESPERA OUVIR, E POR QUE SE ESPERA ──────────────────────────────
# `origem` é a prova de que o termo não foi escolhido a dedo depois de ver o
# resultado. CAPTION = está escrito na legenda pelo autor. ACCOUNT = é o nome da
# conta que publicou. TEMA = é o assunto declarado na própria legenda.
ESPERADO = {
    'C-FanW_CYMz': {
        'conta': '@syngentaitalia', 'idioma': 'it',
        'termos': [
            ('mais', 'CAPTION — a legenda escreve «appassionato di 🌽 Mais»'),
            ('syngenta', 'ACCOUNT — a conta é a da Syngenta Italia'),
            ('discovery seeds', 'CAPTION — a legenda abre com «DISCOVERY SEEDS»'),
        ],
    },
    'Db5QG2Dk3sF': {
        'conta': '@syngenta.es', 'idioma': 'es',
        'termos': [
            ('syngenta', 'CAPTION — a legenda cita «Syngenta es una empresa de '
                         'ciencia agrícola»'),
            ('agricola', 'CAPTION — mesma frase da legenda'),
            ('fitosanitarios', 'TEMA — a fala contrapõe fitossanitários a ciência '
                              'agrícola; o termo é do setor'),
        ],
    },
    'DW6X5lZkU41': {
        'conta': '@syngenta (agronomic service rep)', 'idioma': 'en',
        'termos': [
            ('wheat', 'TEMA — a publicação é sobre trigo em rotação'),
            ('rotation', 'TEMA — a fala explica por que o trigo entra na rotação'),
        ],
    },
    'C2b0GJrIJ8t': {
        'conta': '@rtl_france', 'idioma': 'fr',
        'termos': [
            ('paris', 'TEMA — a pergunta da entrevista é «jusqu\'à bloquer Paris ?»'),
            ('ministre', 'TEMA — a fala cita o primeiro-ministro'),
        ],
    },
}


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s.lower())


def _tem(texto, termo):
    t = _norm(termo)
    if len(t.replace(' ', '')) < 5:
        return re.search(r'(?<![a-z0-9])%s(?![a-z0-9])' % re.escape(t), texto) is not None
    return t in texto


def medir(itens):
    """→ (linhas, resumo). Uma linha por caso, com o denominador à vista."""
    linhas, por_estado = [], {}
    for i in itens:
        sc = i['REEL']['POST_ID']
        alvo = ESPERADO.get(sc)
        texto = _norm(i.get('TRANSCRIPT_TEXT') or '')

        if not alvo:
            # SEM GABARITO NÃO SE DÁ NOTA. Um caso sem termos esperados não é
            # PASS nem FAIL — é um caso que ninguém conferiu, e dizer outra coisa
            # seria fabricar uma medida.
            linhas.append({
                'REEL': sc, 'VEREDITO': 'NAO_CONFERIDO',
                'PORQUE': ('nao ha termos esperados declarados para este caso. '
                           'Isto NAO e reprovacao: e ausencia de gabarito.'),
                'TRANSCRIPT_STATE': i.get('TRANSCRIPT_STATE'),
                'TERMOS_ESPERADOS': 0, 'TERMOS_ENCONTRADOS': 0})
            por_estado['NAO_CONFERIDO'] = por_estado.get('NAO_CONFERIDO', 0) + 1
            continue

        achados = [(t, o, _tem(texto, t)) for t, o in alvo['termos']]
        n_ok = sum(1 for _t, _o, ok in achados if ok)
        n = len(achados)
        veredito = PASS if n_ok == n else (PARTIAL if n_ok else FAIL)
        if i.get('TRANSCRIPT_STATE') != 'OK':
            veredito = FAIL
        linhas.append({
            'REEL': sc, 'CONTA': alvo['conta'], 'IDIOMA': alvo['idioma'],
            'VEREDITO': veredito,
            'TRANSCRIPT_STATE': i.get('TRANSCRIPT_STATE'),
            'ASR_MODEL': (i.get('DERIVED') or {}).get('NOTES', {}).get('ASR_MODEL',
                                                                      'NOT_KNOWN'),
            'TERMOS_ESPERADOS': n,
            'TERMOS_ENCONTRADOS': n_ok,
            'DENOMINADOR': ('%d termos declarados nesta tabela, com origem. '
                            'Nao e taxa de erro por palavra.' % n),
            'TERMOS': [{'TERMO': t, 'ORIGEM': o, 'ENCONTRADO': 'YES' if ok else 'NO'}
                       for t, o, ok in achados],
        })
        por_estado[veredito] = por_estado.get(veredito, 0) + 1
    return linhas, por_estado


def main():
    if not os.path.exists(CORPUS):
        print('sem corpus ainda: %s' % os.path.relpath(CORPUS, ROOT))
        print('Rode `py ferramentas/reel_transcricao.py um --url=...` antes.')
        return 2
    with open(CORPUS, encoding='utf-8') as f:
        d = json.load(f)
    linhas, resumo = medir(d['ITEMS'])

    corpo = {
        'SOURCE_ID': 'REEL-TRANSCRICOES/QUALIDADE-DA-FALA-V1',
        'source': ('conferencia mecanica da fala escrita contra termos esperados '
                   'declarados, com a origem de cada termo'),
        'SOURCE_LOCATION': 'derivado — nenhuma execucao, nenhum custo',
        'FACT_LOCATION': 'NAO_SE_APLICA',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'O_QUE_ISTO_NAO_E': [
            'nao e taxa de erro por palavra (WER): nao ha transcricao oficial destes '
            'Reels, e inventar o denominador seria pior do que nao medir',
            'nao mede fluencia nem pontuacao',
            'PASS quer dizer «os termos que importam apareceram», nao «esta perfeita»',
        ],
        'CASOS': len(linhas),
        'POR_VEREDITO': resumo,
        'LINHAS': linhas,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('CASO          IDIOMA  VEREDITO       TERMOS  MODELO')
    for l in linhas:
        print('%-13s %-7s %-14s %s/%s   %s'
              % (l['REEL'], l.get('IDIOMA', '-'), l['VEREDITO'],
                 l['TERMOS_ENCONTRADOS'], l['TERMOS_ESPERADOS'],
                 l.get('ASR_MODEL', '-')))
        for t in l.get('TERMOS', []):
            if t['ENCONTRADO'] == 'NO':
                print('      FALTOU «%s» — %s' % (t['TERMO'], t['ORIGEM']))
    print()
    print('por veredito: %s' % resumo)
    print('gravado: %s' % os.path.relpath(SAIDA, ROOT))
    return 0 if resumo.get(FAIL, 0) == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
